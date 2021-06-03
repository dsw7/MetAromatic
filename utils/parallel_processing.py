import logging
from re import split
from os import path
from tempfile import gettempdir
from time import time
from datetime import datetime
from concurrent import futures
from signal import signal, SIGINT
from pymongo import MongoClient
from .met_aromatic import MetAromatic
from .consts import (
    EXIT_FAILURE,
    EXIT_SUCCESS,
    MAXIMUM_WORKERS,
    LEN_PDB_CODE,
    DEFAULT_MONGO_HOST,
    DEFAULT_MONGO_PORT,
    DEFAULT_LOGFILE_NAME,
    ISO_8601_DATE_FORMAT,
    LOGRECORD_FORMAT
)

LOG_HANDLERS = [
    logging.FileHandler(path.join(gettempdir(), DEFAULT_LOGFILE_NAME)),
    logging.StreamHandler()
]

logging.basicConfig(
    level=logging.DEBUG,
    format=LOGRECORD_FORMAT,
    datefmt=ISO_8601_DATE_FORMAT,
    handlers=LOG_HANDLERS
)

class RunBatchQueries(MetAromatic):
    def __init__(self, parameters):
        self.parameters = parameters

        MetAromatic.__init__(
            self, self.parameters['cutoff_distance'], self.parameters['cutoff_angle'],
            self.parameters['chain'], self.parameters['model']
        )

        # click does existence check - no need for try / except
        logging.info('Imported pdb codes from file %s', self.parameters['path_batch_file'])
        pdb_codes = []
        with open(self.parameters['path_batch_file']) as batch_file:
            for line in batch_file:
                pdb_codes.extend(
                    [row for row in split(r'(;|,|\s)\s*', line) if len(row) == LEN_PDB_CODE]
                )

        self.number_pdb_codes = len(pdb_codes)

        logging.info('Splitting list of pdb codes into %i chunks', self.parameters['threads'])
        self.chunked_pdb_codes = [
            pdb_codes[i::self.parameters['threads']] for i in range(self.parameters['threads'])
        ]

        self.client = MongoClient(DEFAULT_MONGO_HOST, DEFAULT_MONGO_PORT)
        self.count = 0

        if self.parameters['threads'] > MAXIMUM_WORKERS:
            logging.warning('Number of selected workers exceeds maximum number of workers.')
            logging.warning('The thread pool will use a maximum of %i workers.', MAXIMUM_WORKERS)

        self.batch_job_metadata = {
            'num_workers': self.parameters['threads'],
            'cutoff_distance': self.parameters['cutoff_distance'],
            'cutoff_angle': self.parameters['cutoff_angle'],
            'chain': self.parameters['chain'],
            'model': self.parameters['model'],
            'data_acquisition_date': datetime.now()
        }

        self.bool_disable_workers = False
        signal(SIGINT, self.disable_all_workers)

    def disable_all_workers(self, ipc_signal, frame):
        self.bool_disable_workers = True
        logging.info('Detected SIGINT!')
        logging.info('Attempting to stop all workers!')

    def worker_met_aromatic(self, chunked_list_pdb_codes):
        collection = self.client[self.parameters['database']][self.parameters['collection']]

        for code in chunked_list_pdb_codes:
            if self.bool_disable_workers:
                logging.info('Received interrupt signal - stopping worker thread...')
                break
            try:
                results = self.get_met_aromatic_interactions(code)
            except Exception:  # catch remaining unhandled exceptions
                self.count += 1
                logging.exception('Could not process code: %s. Count: %i', code, self.count)
            else:
                self.count += 1
                logging.info('Processed %s. Count: %i', code, self.count)
                collection.insert(results)

    def deploy_jobs(self):
        if self.parameters['database'] in self.client.list_database_names():
            if self.parameters['collection'] in self.client[self.parameters['database']].list_collection_names():
                logging.error(
                    'Database/collection pair %s.%s exists!',
                    self.parameters['database'],
                    self.parameters['collection']
                )
                return EXIT_FAILURE

        name_collection_info = f"{self.parameters['collection']}_info"
        collection_info = self.client[self.parameters['database']][name_collection_info]

        logging.info('Deploying %i workers!', self.parameters['threads'])

        with futures.ThreadPoolExecutor(max_workers=MAXIMUM_WORKERS) as executor:
            start_time = time()
            workers = [
                executor.submit(self.worker_met_aromatic, chunk) for chunk in self.chunked_pdb_codes
            ]

            if futures.wait(workers, return_when=futures.ALL_COMPLETED):
                execution_time = round(time() - start_time, 3)

                logging.info('Batch job complete!')
                logging.info('Results loaded into database: %s', self.parameters['database'])
                logging.info('Results loaded into collection: %s', self.parameters['collection'])
                logging.info('Batch job statistics loaded into collection: %s', name_collection_info)
                logging.info('Batch job execution time: %f s', execution_time)

                self.batch_job_metadata['batch_job_execution_time'] = execution_time
                self.batch_job_metadata['number_of_entries'] = self.number_pdb_codes

                collection_info.insert(self.batch_job_metadata)

        return EXIT_SUCCESS
