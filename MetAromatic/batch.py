import logging
from re import split
from time import time
from datetime import datetime
from concurrent import futures
from signal import signal, SIGINT
from pymongo import MongoClient, errors, collection
from .consts import PATH_BATCH_LOG, LOGRECORD_FORMAT, ISO_8601_DATE_FORMAT
from .errors import SearchError
from .models import MetAromaticParams, BatchParams
from .pair import MetAromatic

LEN_PDB_CODE = 4
MAXIMUM_WORKERS = 15


def get_collection_handle(bp: BatchParams) -> collection.Collection:
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

    return client[bp.database][bp.collection]


class ParallelProcessing:
    log = logging.getLogger("met-aromatic")

    def __init__(self, params: MetAromaticParams, bp: BatchParams) -> None:
        self.params = params
        self.bp = bp
        self.collection = get_collection_handle(bp)

        self.pdb_codes: list[str] = []
        self.pdb_codes_chunked: list[list[str]] = []
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
        self.collection.database.drop_collection(self.bp.collection)

        info_collection = f"{self.bp.collection}_info"

        self.log.info('Will overwrite collection "%s" if exists', info_collection)
        self.collection.database.drop_collection(info_collection)

    def ensure_collection_does_not_exist(self) -> None:
        collections = self.collection.database.list_collection_names()

        if self.bp.collection in collections:
            raise SearchError(
                'Collection "{self.bp.collection}" exists! Cannot proceed'
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

        if not self.bp.path_batch_file.exists():
            raise SearchError(f"Path {self.bp.path_batch_file} does not exist")

        with open(self.bp.path_batch_file) as f:
            for line in f:
                for row in split(r"(;|,|\s)\s*", line):
                    if len(row) == LEN_PDB_CODE:
                        self.pdb_codes.append(row)

        self.num_codes = len(self.pdb_codes)

        self.log.info("Splitting list of pdb codes into %i chunks", self.bp.threads)

        for i in range(self.bp.threads):
            self.pdb_codes_chunked.append(self.pdb_codes[i :: self.bp.threads])

    def worker_met_aromatic(self, chunk: list[str]) -> None:
        ma = MetAromatic(self.params)

        for code in chunk:
            if self.bool_disable_workers:
                self.log.info("Received interrupt signal - stopping worker thread...")
                break

            status = "Success"
            self.count += 1

            try:
                fs = ma.get_met_aromatic_interactions(code)
            except SearchError as error:
                status = str(error)
                self.log.error(
                    "Could not process code: %s. Count: %i", code, self.count
                )
            else:
                self.log.info("Processed %s. Count: %i", code, self.count)

                # XXX cannot insert Interactions object into MongoDB
                self.collection.insert_one(
                    {
                        "_id": code,
                        "status": status,
                        "results": fs.interactions,
                    }
                )

    def deploy_jobs(self) -> None:
        self.log.info("Deploying %i workers!", self.bp.threads)

        batch_job_metadata = {
            "num_workers": self.bp.threads,
            "data_acquisition_date": datetime.now(),
            **self.params.dict(),
        }

        name_collection_info = f"{self.bp.collection}_info"
        collection_info = self.collection.database[name_collection_info]

        with futures.ThreadPoolExecutor(
            max_workers=MAXIMUM_WORKERS, thread_name_prefix="Batch"
        ) as executor:
            start_time = time()

            workers = [
                executor.submit(self.worker_met_aromatic, chunk)
                for chunk in self.pdb_codes_chunked
            ]

            if futures.wait(workers, return_when=futures.ALL_COMPLETED):
                execution_time = round(time() - start_time, 3)

                self.log.info("Batch job complete!")
                self.log.info("Results loaded into database: %s", self.bp.database)
                self.log.info("Results loaded into collection: %s", self.bp.collection)
                self.log.info(
                    "Batch job statistics loaded into collection: %s",
                    name_collection_info,
                )
                self.log.info("Batch job execution time: %f s", execution_time)

                batch_job_metadata["batch_job_execution_time"] = execution_time
                batch_job_metadata["number_of_entries"] = self.num_codes
                collection_info.insert_one(batch_job_metadata)

    def main(self) -> None:
        self.set_log_filehandler()
        self.drop_collection_if_overwrite_enabled()
        self.ensure_collection_does_not_exist()
        self.register_ipc_signals()
        self.get_pdb_code_chunks()
        self.deploy_jobs()
