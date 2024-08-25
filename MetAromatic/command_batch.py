import logging
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from datetime import datetime
from pathlib import Path
from re import split
from signal import signal, SIGINT
from threading import Lock
from time import time
from pymongo import MongoClient, errors, database
from .algorithm import MetAromatic
from .aliases import RawData
from .consts import PATH_BATCH_LOG, LOGRECORD_FORMAT, ISO_8601_DATE_FORMAT
from .errors import SearchError
from .load_resources import load_pdb_file_from_rscb
from .models import MetAromaticParams, FeatureSpace, BatchParams

LOGGER = logging.getLogger("met-aromatic")


def _add_filehandler_to_log() -> None:
    LOGGER.info('Will log to file "%s"', PATH_BATCH_LOG)

    channel = logging.FileHandler(PATH_BATCH_LOG)
    channel.setFormatter(
        logging.Formatter(fmt=LOGRECORD_FORMAT, datefmt=ISO_8601_DATE_FORMAT)
    )

    LOGGER.addHandler(channel)


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


def _overwrite_collection_if_enabled(db: database.Database, coll: str) -> None:
    LOGGER.info('Will overwrite collection "%s" if exists', coll)
    db.drop_collection(coll)

    info_collection = f"{coll}_info"
    LOGGER.info('Will overwrite collection "%s" if exists', info_collection)

    db.drop_collection(info_collection)


def _ensure_collection_does_not_exist(db: database.Database, coll: str) -> None:
    if coll in db.list_collection_names():
        raise SearchError(f'Collection "{coll}" exists! Cannot proceed')


def _load_pdb_codes(batch_file: Path) -> list[str]:
    if not batch_file.exists():
        raise SearchError(f"Path {batch_file} does not exist")

    pdb_codes = []

    for line in batch_file.read_text().splitlines():
        for code in split(r"(;|,|\s)\s*", line):
            if len(code) == 4:
                pdb_codes.append(code)

    return pdb_codes


def _chunk_pdb_codes(num_chunks: int, pdb_codes: list[str]) -> list[list[str]]:
    chunks = []

    for i in range(num_chunks):
        chunks.append(pdb_codes[i::num_chunks])

    return chunks


class ParallelProcessing:
    mutex = Lock()

    def __init__(
        self, params: MetAromaticParams, bp: BatchParams, db: database.Database
    ) -> None:
        self.params = params
        self.bp = bp
        self.db = db

        self.chunks: list[list[str]] = []
        self.num_codes = 0
        self.count = 0
        self.bool_disable_workers = False

    def disable_all_workers(self, *args) -> None:
        LOGGER.info("Detected SIGINT!")
        LOGGER.info("Attempting to stop all workers!")

        self.bool_disable_workers = True

    def register_ipc_signals(self) -> None:
        LOGGER.info("Registering SIGINT to thread terminator")

        self.bool_disable_workers = False
        signal(SIGINT, self.disable_all_workers)

    def get_pdb_code_chunks(self) -> None:
        LOGGER.info("Imported pdb codes from file %s", self.bp.path_batch_file)

        pdb_codes = _load_pdb_codes(self.bp.path_batch_file)
        self.num_codes = len(pdb_codes)

        LOGGER.info("Splitting list of pdb codes into %i chunks", self.bp.threads)
        self.chunks = _chunk_pdb_codes(self.bp.threads, pdb_codes)

    def worker_met_aromatic(self, chunk: list[str]) -> None:
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

    def deploy_jobs(self) -> None:
        LOGGER.info("Deploying %i workers!", self.bp.threads)

        with ThreadPoolExecutor(max_workers=15, thread_name_prefix="Batch") as executor:
            start_time = time()

            workers = [
                executor.submit(self.worker_met_aromatic, chunk)
                for chunk in self.chunks
            ]

            if wait(workers, return_when=ALL_COMPLETED):
                exec_time = round(time() - start_time, 3)

                LOGGER.info("Batch job complete!")
                LOGGER.info("Results loaded into database: %s", self.bp.database)
                LOGGER.info("Results loaded into collection: %s", self.bp.collection)
                LOGGER.info("Batch job execution time: %f s", exec_time)
                self.insert_summary_doc(exec_time)

    def insert_summary_doc(self, exec_time: float) -> None:
        info_collection = f"{self.bp.collection}_info"

        batch_job_metadata = {
            "batch_job_execution_time": exec_time,
            "data_acquisition_date": datetime.now(),
            "num_workers": self.bp.threads,
            "number_of_entries": self.num_codes,
            **self.params.dict(),
        }

        self.db[info_collection].insert_one(batch_job_metadata)
        LOGGER.info("Statistics loaded into collection: %s", info_collection)

    def main(self) -> None:
        self.register_ipc_signals()
        self.get_pdb_code_chunks()
        self.deploy_jobs()


def run_batch_job(params: MetAromaticParams, bp: BatchParams) -> None:
    _add_filehandler_to_log()

    db = _get_database_handle(bp)

    if bp.overwrite:
        _overwrite_collection_if_enabled(db=db, coll=bp.collection)

    _ensure_collection_does_not_exist(db=db, coll=bp.collection)

    ParallelProcessing(params=params, bp=bp, db=db).main()
