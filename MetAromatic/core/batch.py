import logging
import sys
from re import split
from os import path
from tempfile import gettempdir
from time import time
from datetime import datetime
from concurrent import futures
from signal import signal, SIGINT
from pymongo import (
    MongoClient,
    errors
)
from .helpers.consts import (
    EXIT_FAILURE,
    EXIT_SUCCESS,
    MAXIMUM_WORKERS,
    LEN_PDB_CODE,
    DEFAULT_MONGO_HOST,
    DEFAULT_MONGO_PORT,
    SERVER_TIMEOUT_MSEC,
    DEFAULT_LOGFILE_NAME,
    ISO_8601_DATE_FORMAT,
    LOGRECORD_FORMAT
)
from .pair import MetAromatic

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

class ParallelProcessing:

    def __init__(self, cli_args: dict) -> None:
        self.cli_args = cli_args

        self.client = self._get_mongo_client()

        if self.cli_args['threads'] > MAXIMUM_WORKERS:
            logging.warning('Number of selected workers exceeds maximum number of workers.')
            logging.warning('The thread pool will use a maximum of %i workers.', MAXIMUM_WORKERS)

        self.pdb_codes = []
        self.chunked_pdb_codes = []
        self.count = 0
        self.collection_handle = self.client[self.cli_args['database']][self.cli_args['collection']]
        self.bool_disable_workers = None

        self.batch_job_metadata = {
            'num_workers': self.cli_args['threads'],
            'cutoff_distance': self.cli_args['cutoff_distance'],
            'cutoff_angle': self.cli_args['cutoff_angle'],
            'chain': self.cli_args['chain'],
            'model': self.cli_args['model'],
            'data_acquisition_date': datetime.now()
        }

        self._ensure_collection_does_not_exist()
        self._register_ipc_signals()
        self._read_batch_file()
        self._generate_chunks()

    def _get_mongo_client(self) -> MongoClient:
        logging.info('Handshaking with MongoDB')

        try:
            client = MongoClient(DEFAULT_MONGO_HOST, DEFAULT_MONGO_PORT, serverSelectionTimeoutMS=SERVER_TIMEOUT_MSEC)
            client.server_info()
        except errors.ServerSelectionTimeoutError:
            logging.error('Could not connect to MongoDB on host %s and port %i', DEFAULT_MONGO_HOST, DEFAULT_MONGO_PORT)
            logging.error('Either MongoDB is not installed or the socket address is invalid')
            sys.exit(EXIT_FAILURE)

        return client

    def _ensure_collection_does_not_exist(self) -> None:
        collections = self.client[self.cli_args['database']].list_collection_names()

        if self.cli_args['collection'] in collections:
            logging.error('Collection %s exists!', self.cli_args['collection'])
            sys.exit(EXIT_FAILURE)

    def _disable_all_workers(self, ipc_signal, frame) -> None:
        logging.info('Detected SIGINT!')
        logging.info('Attempting to stop all workers!')

        self.bool_disable_workers = True

    def _register_ipc_signals(self) -> None:
        logging.info('Registering SIGINT to thread terminator')

        self.bool_disable_workers = False
        signal(SIGINT, self._disable_all_workers)

    def _read_batch_file(self) -> None:
        # Click does existence check - no need for try / except
        logging.info('Imported pdb codes from file %s', self.cli_args['path_batch_file'])

        with open(self.cli_args['path_batch_file']) as batch_file:
            for line in batch_file:
                self.pdb_codes.extend(
                    [row for row in split(r'(;|,|\s)\s*', line) if len(row) == LEN_PDB_CODE]
                )

    def _generate_chunks(self) -> None:
        logging.info('Splitting list of pdb codes into %i chunks', self.cli_args['threads'])

        self.chunked_pdb_codes = [
            self.pdb_codes[i::self.cli_args['threads']] for i in range(self.cli_args['threads'])
        ]

    def worker_met_aromatic(self, chunk: list) -> None:

        handle_ma = MetAromatic(
            self.cli_args['cutoff_distance'],
            self.cli_args['cutoff_angle'],
            self.cli_args['chain'],
            self.cli_args['model']
        )

        for code in chunk:
            if self.bool_disable_workers:
                logging.info('Received interrupt signal - stopping worker thread...')
                break

            try:
                results = handle_ma.get_met_aromatic_interactions(code)
            except Exception:  # catch remaining unhandled exceptions
                self.count += 1
                logging.exception('Could not process code: %s. Count: %i', code, self.count)
            else:
                self.count += 1
                logging.info('Processed %s. Count: %i', code, self.count)
                self.collection_handle.insert(results)

    def deploy_jobs(self) -> int:
        logging.info('Deploying %i workers!', self.cli_args['threads'])

        name_collection_info = '{}_info'.format(self.cli_args['collection'])
        collection_info = self.client[self.cli_args['database']][name_collection_info]

        with futures.ThreadPoolExecutor(max_workers=MAXIMUM_WORKERS) as executor:
            start_time = time()

            workers = [
                executor.submit(self.worker_met_aromatic, chunk) for chunk in self.chunked_pdb_codes
            ]

            if futures.wait(workers, return_when=futures.ALL_COMPLETED):
                execution_time = round(time() - start_time, 3)

                logging.info('Batch job complete!')
                logging.info('Results loaded into database: %s', self.cli_args['database'])
                logging.info('Results loaded into collection: %s', self.cli_args['collection'])
                logging.info('Batch job statistics loaded into collection: %s', name_collection_info)
                logging.info('Batch job execution time: %f s', execution_time)

                self.batch_job_metadata['batch_job_execution_time'] = execution_time
                self.batch_job_metadata['number_of_entries'] = len(self.pdb_codes)
                collection_info.insert(self.batch_job_metadata)

        return EXIT_SUCCESS
