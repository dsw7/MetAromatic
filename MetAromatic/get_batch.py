from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from datetime import datetime
from json import dumps
from logging import getLogger, config
from pathlib import Path
from re import split
from signal import signal, SIGINT, SIG_DFL
from threading import Lock
from time import time
from typing import Any
from pymongo import MongoClient, errors, database
from .algorithm import MetAromatic
from .aliases import RawData, PdbCodes, Chunks
from .errors import SearchError
from .load_resources import load_pdb_file_from_rscb
from .models import (
    MetAromaticParams,
    FeatureSpace,
    BatchParams,
    BatchResult,
    DictInteractions,
)

Logger = getLogger("met-aromatic")


def _configure_logger() -> None:
    config.dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "%(asctime)s %(threadName)s %(levelname)s %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "met-aromatic": {
                    "handlers": ["console"],
                    "level": "INFO",
                },
            },
        }
    )


def _load_pdb_codes(batch_file: Path) -> PdbCodes:
    Logger.info("Importing pdb codes from file %s", batch_file)

    if not batch_file.exists():
        raise SearchError(f"Path {batch_file} does not exist")

    pdb_codes = []

    for line in batch_file.read_text().splitlines():
        for code in split(r"(;|,|\s)\s*", line):
            if len(code) == 4:
                pdb_codes.append(code)

    return pdb_codes


def _chunk_pdb_codes(num_chunks: int, pdb_codes: PdbCodes) -> Chunks:
    Logger.info("Splitting list of PDB codes into %i chunks", num_chunks)

    chunks = []

    for i in range(num_chunks):
        chunks.append(pdb_codes[i::num_chunks])

    return chunks


def _get_database_handle(bp: BatchParams) -> database.Database:
    client: MongoClient = MongoClient(
        host=bp.host,
        password=bp.password,
        port=bp.port,
        serverSelectionTimeoutMS=1000,
        username=bp.username,
    )

    try:
        client[bp.database].list_collection_names()
    except errors.ServerSelectionTimeoutError as error:
        raise SearchError("Failed to connect to MongoDB") from error
    except errors.OperationFailure as error:
        if error.details is None:
            errmsg = "Unknown error occurred when connecting to MongoDB"
        else:
            errmsg = error.details["errmsg"]
        raise SearchError(errmsg) from error

    return client[bp.database]


def _get_info_collection(base_collection: str) -> str:
    return f"{base_collection}_info"


def _overwrite_collection_if_enabled(db: database.Database, coll: str) -> None:
    Logger.info('Will overwrite collection "%s" if exists', coll)
    db.drop_collection(coll)

    info_collection = _get_info_collection(coll)
    Logger.info('Will overwrite collection "%s" if exists', info_collection)

    db.drop_collection(info_collection)


def _ensure_collection_does_not_exist(db: database.Database, coll: str) -> None:
    if coll in db.list_collection_names():
        raise SearchError(f'Collection "{coll}" exists! Cannot proceed')


class ParallelProcessing:
    mutex = Lock()

    def __init__(
        self,
        params: MetAromaticParams,
        bp: BatchParams,
        db: database.Database,
        chunks: Chunks,
    ) -> None:
        self.params = params
        self.bp = bp
        self.db = db
        self.chunks = chunks

        self.count = 0
        self.disable_workers = False

    def _disable_all_workers(self, *args: Any) -> None:
        Logger.info("Detected SIGINT!")
        Logger.info("Attempting to stop all workers!")

        self.disable_workers = True
        self._unregister_sigint()

    def _register_sigint(self) -> None:
        Logger.info("Registering SIGINT to thread terminator")

        self.disable_workers = False
        signal(SIGINT, self._disable_all_workers)

    def _unregister_sigint(self) -> None:
        Logger.info("Unregistering SIGINT from thread terminator")
        signal(SIGINT, SIG_DFL)

    def _get_interaction(self, code: str) -> BatchResult:
        errmsg: str | None = None
        interactions: list[DictInteractions] | None = None

        try:
            raw_data: RawData = load_pdb_file_from_rscb(code)
            fs: FeatureSpace = MetAromatic(
                params=self.params, raw_data=raw_data
            ).get_interactions()
        except SearchError as error:
            errmsg = str(error)
        except Exception as error:  # pylint: disable=broad-exception-caught
            errmsg = str(error)
        else:
            interactions = fs.serialize_interactions()

        return BatchResult(_id=code, errmsg=errmsg, interactions=interactions)

    def _loop_over_chunk(self, chunk: PdbCodes) -> None:
        collection = self.db[self.bp.collection]

        for code in chunk:
            if self.disable_workers:
                Logger.info("Received interrupt signal - stopping worker thread...")
                break

            with self.mutex:
                self.count += 1

            Logger.info("Processing %s. Count: %i", code, self.count)

            doc_interactions: BatchResult = self._get_interaction(code)
            collection.insert_one(doc_interactions)

    def _insert_summary_doc(self, exec_time: float) -> None:
        batch_job_metadata = {
            "batch_job_execution_time": exec_time,
            "data_acquisition_date": datetime.now(),
            "num_workers": self.bp.threads,
            "number_of_entries": self.count,
            **self.params.dict(),
        }

        info_collection = _get_info_collection(self.bp.collection)

        Logger.info(
            "Loading:\n%s\nInto collection: %s",
            dumps(batch_job_metadata, indent=4, default=str),
            info_collection,
        )

        self.db[info_collection].insert_one(batch_job_metadata)

    def deploy_jobs(self) -> None:
        Logger.info("Deploying %i workers!", self.bp.threads)

        self._register_sigint()

        with ThreadPoolExecutor(max_workers=15, thread_name_prefix="Batch") as executor:
            start_time = time()

            workers = [
                executor.submit(self._loop_over_chunk, chunk) for chunk in self.chunks
            ]

            if wait(workers, return_when=ALL_COMPLETED):
                exec_time = round(time() - start_time, 3)

                Logger.info("Batch job complete!")
                Logger.info("Results loaded into database: %s", self.bp.database)
                Logger.info("Results loaded into collection: %s", self.bp.collection)
                Logger.info("Batch job execution time: %f s", exec_time)
                self._insert_summary_doc(exec_time)

        self._unregister_sigint()


def run_batch_job(params: MetAromaticParams, bp: BatchParams) -> None:
    _configure_logger()

    pdb_codes = _load_pdb_codes(bp.path_batch_file)
    chunks = _chunk_pdb_codes(num_chunks=bp.threads, pdb_codes=pdb_codes)

    db = _get_database_handle(bp)

    if bp.overwrite:
        _overwrite_collection_if_enabled(db=db, coll=bp.collection)

    _ensure_collection_does_not_exist(db=db, coll=bp.collection)

    ParallelProcessing(params=params, bp=bp, db=db, chunks=chunks).deploy_jobs()
