import logging
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from datetime import datetime
from pathlib import Path
from re import split
from signal import signal, SIGINT
from time import time
from pymongo import MongoClient, errors, database
from .consts import PATH_BATCH_LOG, LOGRECORD_FORMAT, ISO_8601_DATE_FORMAT
from .errors import SearchError
from .models import MetAromaticParams, FeatureSpace, BatchParams
from .pair import MetAromatic


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
    log = logging.getLogger("met-aromatic")

    def __init__(self, params: MetAromaticParams, bp: BatchParams) -> None:
        self.params = params
        self.bp = bp
        self.database = _get_database_handle(bp)

        self.chunks: list[list[str]] = []
        self.num_codes = 0
        self.count = 0
        self.bool_disable_workers = False

    def set_log_filehandler(self) -> None:
        self.log.info('Will log to file "%s"', PATH_BATCH_LOG)

        channel = logging.FileHandler(PATH_BATCH_LOG)
        channel.setFormatter(
            logging.Formatter(fmt=LOGRECORD_FORMAT, datefmt=ISO_8601_DATE_FORMAT)
        )

        self.log.addHandler(channel)

    def drop_collection_if_overwrite_enabled(self) -> None:
        if not self.bp.overwrite:
            return

        self.log.info('Will overwrite collection "%s" if exists', self.bp.collection)
        self.database.drop_collection(self.bp.collection)

        info_collection = f"{self.bp.collection}_info"

        self.log.info('Will overwrite collection "%s" if exists', info_collection)
        self.database.drop_collection(info_collection)

    def ensure_collection_does_not_exist(self) -> None:
        if self.bp.collection in self.database.list_collection_names():
            raise SearchError(
                f'Collection "{self.bp.collection}" exists! Cannot proceed'
            )

    def disable_all_workers(self, *args) -> None:
        self.log.info("Detected SIGINT!")
        self.log.info("Attempting to stop all workers!")

        self.bool_disable_workers = True

    def register_ipc_signals(self) -> None:
        self.log.info("Registering SIGINT to thread terminator")

        self.bool_disable_workers = False
        signal(SIGINT, self.disable_all_workers)

    def get_pdb_code_chunks(self) -> None:
        self.log.info("Imported pdb codes from file %s", self.bp.path_batch_file)

        pdb_codes = _load_pdb_codes(self.bp.path_batch_file)
        self.num_codes = len(pdb_codes)

        self.log.info("Splitting list of pdb codes into %i chunks", self.bp.threads)
        self.chunks = _chunk_pdb_codes(self.bp.threads, pdb_codes)

    def worker_met_aromatic(self, chunk: list[str]) -> None:
        ma = MetAromatic(self.params)
        collection = self.database[self.bp.collection]

        for code in chunk:
            if self.bool_disable_workers:
                self.log.info("Received interrupt signal - stopping worker thread...")
                break

            self.count += 1
            self.log.info("Processing %s. Count: %i", code, self.count)

            doc = {"_id": code}

            try:
                fs: FeatureSpace = ma.get_met_aromatic_interactions(code)
            except SearchError as error:
                doc["errmsg"] = str(error)
            else:
                doc["results"] = fs.serialize_interactions()  # type: ignore

            collection.insert_one(doc)

    def deploy_jobs(self) -> None:
        self.log.info("Deploying %i workers!", self.bp.threads)

        with ThreadPoolExecutor(max_workers=15, thread_name_prefix="Batch") as executor:
            start_time = time()

            workers = [
                executor.submit(self.worker_met_aromatic, chunk)
                for chunk in self.chunks
            ]

            if wait(workers, return_when=ALL_COMPLETED):
                exec_time = round(time() - start_time, 3)

                self.log.info("Batch job complete!")
                self.log.info("Results loaded into database: %s", self.bp.database)
                self.log.info("Results loaded into collection: %s", self.bp.collection)
                self.log.info("Batch job execution time: %f s", exec_time)
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

        self.database[info_collection].insert_one(batch_job_metadata)
        self.log.info("Statistics loaded into collection: %s", info_collection)

    def main(self) -> None:
        self.set_log_filehandler()
        self.drop_collection_if_overwrite_enabled()
        self.ensure_collection_does_not_exist()
        self.register_ipc_signals()
        self.get_pdb_code_chunks()
        self.deploy_jobs()
