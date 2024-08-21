import logging
import sys
from re import split
from os import path
from time import time
from datetime import datetime
from concurrent import futures
from signal import signal, SIGINT
from pymongo import MongoClient, errors, collection
from MetAromatic.pair import MetAromatic
from .consts import TMPDIR, LOGRECORD_FORMAT, ISO_8601_DATE_FORMAT
from .models import MetAromaticParams, BatchParams

LEN_PDB_CODE = 4
MAXIMUM_WORKERS = 15


class ParallelProcessing:
    log = logging.getLogger("met-aromatic")

    def __init__(self, params: MetAromaticParams, bp: BatchParams) -> None:
        self.params = params
        self.bp = bp
        self.collection: collection.Collection

        self.pdb_codes: list[str] = []
        self.pdb_codes_chunked: list[list[str]] = []
        self.num_codes = 0
        self.count = 0
        self.bool_disable_workers = False

    def set_log_filehandler(self) -> None:
        self.log.debug("Setting up additional logger")

        logfile_name = path.join(TMPDIR, "met_aromatic.log")
        self.log.info('Will log to file "%s"', logfile_name)

        channel = logging.FileHandler(logfile_name)
        formatter = logging.Formatter(
            fmt=LOGRECORD_FORMAT, datefmt=ISO_8601_DATE_FORMAT
        )
        channel.setFormatter(formatter)

        self.log.addHandler(channel)

    def get_collection_handle(self) -> None:
        client: MongoClient = MongoClient(
            host=self.bp.host,
            password=self.bp.password,
            port=self.bp.port,
            serverSelectionTimeoutMS=1000,
            username=self.bp.username,
        )

        try:
            client.list_databases()
        except (errors.ServerSelectionTimeoutError, errors.OperationFailure):
            self.log.exception("A MongoDB exception occurred")
            sys.exit("Batch job failed")

        self.collection = client[self.bp.database][self.bp.collection]

    def drop_collection_if_overwrite_enabled(self) -> None:
        if not self.bp.overwrite:
            return

        self.log.debug('Will overwrite collection "%s" if exists', self.bp.collection)
        self.collection.database.drop_collection(self.bp.collection)

        info_collection = f"{self.bp.collection}_info"

        self.log.debug('Will overwrite collection "%s" if exists', info_collection)
        self.collection.database.drop_collection(info_collection)

    def ensure_collection_does_not_exist(self) -> None:
        collections = self.collection.database.list_collection_names()

        if self.bp.collection in collections:
            self.log.error('Collection "%s" exists! Cannot proceed', self.bp.collection)
            sys.exit("Batch job failed")

    def disable_all_workers(self, *args) -> None:
        self.log.info("Detected SIGINT!")
        self.log.info("Attempting to stop all workers!")

        self.bool_disable_workers = True

    def register_ipc_signals(self) -> None:
        self.log.debug("Registering SIGINT to thread terminator")

        self.bool_disable_workers = False
        signal(SIGINT, self.disable_all_workers)

    def get_pdb_code_chunks(self) -> None:
        self.log.info("Imported pdb codes from file %s", self.bp.path_batch_file)

        if not path.exists(self.bp.path_batch_file):
            sys.exit(f"Path {self.bp.path_batch_file} does not exist")

        with open(self.bp.path_batch_file) as f:
            for line in f:
                for row in split(r"(;|,|\s)\s*", line):
                    if len(row) == LEN_PDB_CODE:
                        self.pdb_codes.append(row)

        self.num_codes = len(self.pdb_codes)

        self.log.debug("Splitting list of pdb codes into %i chunks", self.bp.threads)

        for i in range(self.bp.threads):
            self.pdb_codes_chunked.append(self.pdb_codes[i :: self.bp.threads])

    def worker_met_aromatic(self, chunk: list[str]) -> None:
        handle_ma = MetAromatic(self.params)

        for code in chunk:
            if self.bool_disable_workers:
                self.log.debug("Received interrupt signal - stopping worker thread...")
                break

            try:
                fs = handle_ma.get_met_aromatic_interactions(code)
                results = {
                    "_id": code,
                    "ok": fs.OK,
                    "status": fs.status,
                    "results": fs.interactions,
                }
            except Exception:
                self.count += 1
                self.log.exception(
                    "Could not process code: %s. Count: %i", code, self.count
                )
            else:
                self.count += 1
                self.log.info("Processed %s. Count: %i", code, self.count)
                self.collection.insert_one(results)

    def deploy_jobs(self) -> None:
        self.log.debug("Deploying %i workers!", self.bp.threads)

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
        self.get_collection_handle()
        self.drop_collection_if_overwrite_enabled()
        self.ensure_collection_does_not_exist()
        self.register_ipc_signals()
        self.get_pdb_code_chunks()
        self.deploy_jobs()
