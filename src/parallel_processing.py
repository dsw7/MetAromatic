import sys
import logging
from os import path
from re import split
from time import time
from datetime import datetime
from concurrent import futures
from tempfile import gettempdir
from pymongo import MongoClient
from numpy import array_split
from met_aromatic import MetAromatic
from consts import (
    EXIT_FAILURE,
    MAXIMUM_WORKERS,
    LEN_PDB_CODE,
    DEFAULT_MONGO_HOST,
    DEFAULT_MONGO_PORT
)


class Logging:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s:%(asctime)s: %(message)s',
            datefmt='%d-%b-%y:%H:%M:%S',
            handlers=[
                logging.FileHandler(path.join(gettempdir(), 'met_aromatic.log'), 'w'),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger()

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def exception(self, message):
        self.logger.exception(message)

    def error(self, message):
        self.logger.error(message)


class RunBatchQueries:
    def __init__(self, path_batch_file, cutoff_distance, cutoff_angle,
                 chain, model, threads, collection, database):
        self.batch_file = path_batch_file
        self.cutoff_distance = cutoff_distance
        self.cutoff_angle = cutoff_angle
        self.chain = chain
        self.model = model
        self.num_workers = threads
        self.collection_name = collection
        self.database_name = database
        self.client = MongoClient(DEFAULT_MONGO_HOST, DEFAULT_MONGO_PORT)
        self.count = 0
        self.logger = Logging()

        if self.num_workers > MAXIMUM_WORKERS:
            self.logger.warning('Number of selected workers exceeds maximum number of workers.')
            self.logger.warning(f'The thread pool will use a maximum of {MAXIMUM_WORKERS} workers.')

    def open_batch_file(self):
        # click does existence check - no need for try / except
        pdb_codes = []
        with open(self.batch_file) as batch:
            for line in batch:
                pdb_codes.extend([i for i in split(r'(;|,|\s)\s*', line) if len(i) == LEN_PDB_CODE])
        return pdb_codes

    def prepare_batch_job_info(self, execution_time, number_entries):
        return {
            'num_workers': self.num_workers,
            'cutoff_distance': self.cutoff_distance,
            'cutoff_angle': self.cutoff_angle,
            'chain': self.chain,
            'model': self.model,
            'batch_job_execution_time': execution_time,
            'data_acquisition_date': datetime.now(),
            'number_of_entries': number_entries
        }

    def worker(self, list_codes):
        collection_results = self.client[self.database_name][self.collection_name]

        for code in list_codes:
            try:
                results = MetAromatic(
                    code=code,
                    cutoff_distance=self.cutoff_distance,
                    cutoff_angle=self.cutoff_angle,
                    chain=self.chain,
                    model=self.model
                ).get_met_aromatic_interactions()
            except Exception:  # catch remaining unhandled exceptions
                self.count += 1
                self.logger.exception(f'Could not process code: {code}. Count: {self.count}')
            else:
                self.count += 1
                self.logger.info(f'Processed {code}. Count: {self.count}')
                collection_results.insert(results)

    def database_collection_exists(self):
        retval = True
        if self.database_name in self.client.list_database_names():
            if not self.collection_name in self.client[self.database_name].list_collection_names():
                retval = False
        else:
            retval = False
        return retval

    def deploy_jobs(self):
        if self.database_collection_exists():
            self.logger.error(f'Database/collection pair {self.database_name}.{self.collection_name} exists.')
            self.logger.error('Use a different collection name.')
            sys.exit(EXIT_FAILURE)

        pdb_codes = self.open_batch_file()
        chunked_pdb_codes = array_split(pdb_codes, self.num_workers)

        name_collection_info = f'{self.collection_name}_info'
        collection_info = self.client[self.database_name][name_collection_info]

        self.logger.info(f'Deploying {self.num_workers} workers!')

        with futures.ThreadPoolExecutor(max_workers=MAXIMUM_WORKERS) as executor:
            start_time = time()
            workers = [
                executor.submit(self.worker, chunk) for chunk in chunked_pdb_codes
            ]

            if futures.wait(workers, return_when=futures.ALL_COMPLETED):
                self.logger.info('Batch job complete!')
                self.logger.info(f'Results loaded into database: {self.database_name}')
                self.logger.info(f'Results loaded into collection: {self.collection_name}')
                self.logger.info(f'Batch job statistics loaded into collection: {name_collection_info}')

                collection_info.insert(
                    self.prepare_batch_job_info(
                        time() - start_time,
                        len(pdb_codes)
                    )
                )
