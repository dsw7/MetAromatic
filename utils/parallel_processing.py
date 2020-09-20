import sys
import logging
from os import path
from re import split
from time import time
from datetime import datetime
from concurrent import futures
from tempfile import gettempdir
from pymongo import MongoClient
from .met_aromatic import MetAromatic
from .consts import (
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
            filename = DEFAULT_LOGFILE_NAME

        self.filepath = path.join(gettempdir(), filename)
        print(f'Batch job progress logged to: {self.filepath}')

    def get_log_handle(self):
        self.formatter = logging.Formatter(
            '%(levelname)s:%(asctime)s: %(message)s',
            datefmt='%d-%b-%y:%H:%M:%S',
        )
        handler = logging.FileHandler(self.filepath, 'w')
        handler.setFormatter(self.formatter)

        logger = logging.getLogger()
        logger.setLevel(LOG_LEVEL)
        logger.addHandler(handler)
        return logger


class RunBatchQueries(Logger):
    def __init__(self, parameters):
        self.parameters = parameters

        print('Starting batch job...')

        super().__init__()
        self.logger = self.get_log_handle()

        # click does existence check - no need for try / except
        self.logger.info('Imported pdb codes from file %s', self.parameters['path_batch_file'])
        pdb_codes = []
        with open(self.parameters['path_batch_file']) as batch_file:
            for line in batch_file:
                pdb_codes.extend(
                    [row for row in split(r'(;|,|\s)\s*', line) if len(row) == LEN_PDB_CODE]
                )

        self.number_pdb_codes = len(pdb_codes)

        self.logger.info('Splitting list of pdb codes into %i chunks', self.parameters['threads'])
        self.chunked_pdb_codes = [
            pdb_codes[i::self.parameters['threads']] for i in range(self.parameters['threads'])
        ]

        self.client = MongoClient(DEFAULT_MONGO_HOST, DEFAULT_MONGO_PORT)
        self.count = 0

        if self.parameters['threads'] > MAXIMUM_WORKERS:
            self.logger.warning('Number of selected workers exceeds maximum number of workers.')
            self.logger.warning('The thread pool will use a maximum of %i workers.', MAXIMUM_WORKERS)

        self.batch_job_metadata = {
            'num_workers': self.parameters['threads'],
            'cutoff_distance': self.parameters['cutoff_distance'],
            'cutoff_angle': self.parameters['cutoff_angle'],
            'chain': self.parameters['chain'],
            'model': self.parameters['model'],
            'data_acquisition_date': datetime.now()
        }

    def worker(self, list_codes):
        collection_results = self.client[self.parameters['database']][self.parameters['collection']]

        for code in list_codes:
            try:
                results = MetAromatic(
                    code=code,
                    cutoff_distance=self.parameters['cutoff_distance'],
                    cutoff_angle=self.parameters['cutoff_angle'],
                    chain=self.parameters['chain'],
                    model=self.parameters['model']
                ).get_met_aromatic_interactions()
            except Exception:  # catch remaining unhandled exceptions
                self.count += 1
                self.logger.exception('Could not process code: %s. Count: %i', code, self.count)
            else:
                self.count += 1
                self.logger.info('Processed %s. Count: %i', code, self.count)
                collection_results.insert(results)

    def database_collection_exists(self):
        retval = True
        if self.parameters['database'] in self.client.list_database_names():
            if not self.parameters['collection'] in self.client[self.parameters['database']].list_collection_names():
                retval = False
        else:
            retval = False
        return retval

    def deploy_jobs(self):
        if self.database_collection_exists():
            err_str = f'Database/collection pair {self.parameters["database"]}.{self.parameters["collection"]} exists!'
            self.logger.error(err_str)
            print(err_str, file=sys.stderr)
            sys.exit(EXIT_FAILURE)

        name_collection_info = f"{self.parameters['collection']}_info"
        collection_info = self.client[self.parameters['database']][name_collection_info]

        self.logger.info('Deploying %i workers!', self.parameters['threads'])

        with futures.ThreadPoolExecutor(max_workers=MAXIMUM_WORKERS) as executor:
            start_time = time()
            workers = [
                executor.submit(self.worker, chunk) for chunk in self.chunked_pdb_codes
            ]

            if futures.wait(workers, return_when=futures.ALL_COMPLETED):
                self.logger.info('Batch job complete!')
                self.logger.info('Results loaded into database: %s', self.parameters['database'])
                self.logger.info('Results loaded into collection: %s', self.parameters['collection'])
                self.logger.info('Batch job statistics loaded into collection: %s', name_collection_info)

                self.batch_job_metadata['batch_job_execution_time'] = time() - start_time
                self.batch_job_metadata['number_of_entries'] = self.number_pdb_codes

                collection_info.insert(self.batch_job_metadata)

        print('Batch job complete!')
