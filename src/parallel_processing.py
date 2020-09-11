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
    DEFAULT_MONGO_PORT,
    DEFAULT_LOGFILE_NAME,
    LOG_LEVEL
)


class Logger:
    def __init__(self, filename=None):
        if not filename:
            self.filename = DEFAULT_LOGFILE_NAME
        else:
            self.filename = filename

    def get_log_handle(self):
        self.formatter = logging.Formatter(
            '%(levelname)s:%(asctime)s: %(message)s',
            datefmt='%d-%b-%y:%H:%M:%S',
        )
        handler = logging.FileHandler(path.join(gettempdir(), self.filename), 'w')
        handler.setFormatter(self.formatter)

        logger = logging.getLogger()
        logger.setLevel(LOG_LEVEL)
        logger.addHandler(handler)
        return logger


class RunBatchQueries(Logger):
    def __init__(self, path_batch_file, cutoff_distance, cutoff_angle,
                 chain, model, threads, collection, database):

        super().__init__(None)
        self.logger = self.get_log_handle()

        # click does existence check - no need for try / except
        self.pdb_codes = []
        with open(path_batch_file) as batch_file:
            for line in batch_file:
                self.pdb_codes.extend(
                    [row for row in split(r'(;|,|\s)\s*', line) if len(row) == LEN_PDB_CODE]
                )

        self.cutoff_distance = cutoff_distance
        self.cutoff_angle = cutoff_angle
        self.chain = chain
        self.model = model
        self.num_workers = threads
        self.collection_name = collection
        self.database_name = database

        self.client = MongoClient(DEFAULT_MONGO_HOST, DEFAULT_MONGO_PORT)
        self.count = 0

        if self.num_workers > MAXIMUM_WORKERS:
            self.logger.warning('Number of selected workers exceeds maximum number of workers.')
            self.logger.warning(f'The thread pool will use a maximum of {MAXIMUM_WORKERS} workers.')

        self.batch_job_metadata = {
            'num_workers': self.num_workers,
            'cutoff_distance': self.cutoff_distance,
            'cutoff_angle': self.cutoff_angle,
            'chain': self.chain,
            'model': self.model,
            'data_acquisition_date': datetime.now()
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

        chunked_pdb_codes = array_split(self.pdb_codes, self.num_workers)

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

                self.batch_job_metadata['batch_job_execution_time'] = time() - start_time
                self.batch_job_metadata['number_of_entries'] = len(self.pdb_codes)

                collection_info.insert(self.batch_job_metadata)
