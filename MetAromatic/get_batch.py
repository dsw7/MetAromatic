from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from datetime import datetime
from json import dumps
from logging import getLogger
from pathlib import Path
from re import split
from signal import signal, SIGINT, SIG_DFL
from threading import Lock
from time import time
from pymongo import MongoClient, errors, database
from .algorithm import MetAromatic
from .aliases import RawData, PdbCodes, Chunks
from .consts import PATH_BATCH_LOG
from .errors import SearchError
from .load_resources import load_pdb_file_from_rscb
from .models import MetAromaticParams, FeatureSpace, BatchParams

LOGGER = getLogger("met-aromatic")


def _load_pdb_codes(batch_file: Path) -> PdbCodes:
    LOGGER.info("Importing pdb codes from file %s", batch_file)

    if not batch_file.exists():
        raise SearchError(f"Path {batch_file} does not exist")

    pdb_codes = []

    for line in batch_file.read_text().splitlines():
        for code in split(r"(;|,|\s)\s*", line):
            if len(code) == 4:
                pdb_codes.append(code)

    return pdb_codes


def _chunk_pdb_codes(num_chunks: int, pdb_codes: PdbCodes) -> Chunks:
    LOGGER.info("Splitting list of PDB codes into %i chunks", num_chunks)

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
    LOGGER.info('Will overwrite collection "%s" if exists', coll)
    db.drop_collection(coll)

    info_collection = _get_info_collection(coll)
    LOGGER.info('Will overwrite collection "%s" if exists', info_collection)

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
        self.bool_disable_workers = False

    def _disable_all_workers(self, *args) -> None:
        LOGGER.info("Detected SIGINT!")
        LOGGER.info("Attempting to stop all workers!")

        self.bool_disable_workers = True
        self._unregister_sigint()

    def _register_sigint(self) -> None:
        LOGGER.info("Registering SIGINT to thread terminator")

        self.bool_disable_workers = False
        signal(SIGINT, self._disable_all_workers)

    def _unregister_sigint(self) -> None:
        LOGGER.info("Unregistering SIGINT from thread terminator")
        signal(SIGINT, SIG_DFL)

    def _loop_over_chunk(self, chunk: PdbCodes) -> None:
        collection = self.db[self.bp.collection]

        for code in chunk:
            if self.bool_disable_workers:
                LOGGER.info("Received interrupt signal - stopping worker thread...")
                break

            with self.mutex:
                self.count += 1

            LOGGER.info("Processing %s. Count: %i", code, self.count)
            doc = {"_id": code}

            try:
                raw_data: RawData = load_pdb_file_from_rscb(code)
                fs: FeatureSpace = MetAromatic(
                    params=self.params, raw_data=raw_data
                ).get_interactions()
            except SearchError as error:
                doc["errmsg"] = str(error)
            else:
                doc["results"] = fs.serialize_interactions()  # type: ignore

            collection.insert_one(doc)

    def _insert_summary_doc(self, exec_time: float) -> None:
        batch_job_metadata = {
            "batch_job_execution_time": exec_time,
            "data_acquisition_date": datetime.now(),
            "num_workers": self.bp.threads,
            "number_of_entries": self.count,
            **self.params.dict(),
        }

        info_collection = _get_info_collection(self.bp.collection)

        LOGGER.info(
            "Loading:\n%s\nInto collection: %s",
            dumps(batch_job_metadata, indent=4, default=str),
            info_collection,
        )

        self.db[info_collection].insert_one(batch_job_metadata)

    def deploy_jobs(self) -> None:
        LOGGER.info("Deploying %i workers!", self.bp.threads)

        self._register_sigint()

        with ThreadPoolExecutor(max_workers=15, thread_name_prefix="Batch") as executor:
            start_time = time()

            workers = [
                executor.submit(self._loop_over_chunk, chunk) for chunk in self.chunks
            ]

            if wait(workers, return_when=ALL_COMPLETED):
                exec_time = round(time() - start_time, 3)

                LOGGER.info("Batch job complete!")
                LOGGER.info("Results loaded into database: %s", self.bp.database)
                LOGGER.info("Results loaded into collection: %s", self.bp.collection)
                LOGGER.info("Batch job execution time: %f s", exec_time)
                self._insert_summary_doc(exec_time)

        self._unregister_sigint()


def run_batch_job(params: MetAromaticParams, bp: BatchParams) -> None:
    LOGGER.info('Will log to file "%s"', PATH_BATCH_LOG)

    pdb_codes = _load_pdb_codes(bp.path_batch_file)
    chunks = _chunk_pdb_codes(num_chunks=bp.threads, pdb_codes=pdb_codes)

    db = _get_database_handle(bp)

    if bp.overwrite:
        _overwrite_collection_if_enabled(db=db, coll=bp.collection)

    _ensure_collection_does_not_exist(db=db, coll=bp.collection)

    ParallelProcessing(params=params, bp=bp, db=db, chunks=chunks).deploy_jobs()
