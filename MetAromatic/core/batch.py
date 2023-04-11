import logging
import sys
from typing import List, Dict, Union
from re import split
from os import path
from tempfile import gettempdir
from time import time
from datetime import datetime
from concurrent import futures
from signal import signal, SIGINT
from pymongo import MongoClient, errors
from core.helpers.consts import T
from .pair import MetAromatic

ISO_8601_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
LOGRECORD_FORMAT = '%(asctime)s %(levelname)5s [ %(funcName)s ] %(message)s'
LOGFILE_NAME = path.join(gettempdir(), 'met_aromatic.log')
LEN_PDB_CODE = 4
MAXIMUM_WORKERS = 15
TIMEOUT_MSEC_MONGODB = 1000

logging.basicConfig(
    level=logging.DEBUG,
    format=LOGRECORD_FORMAT,
    datefmt=ISO_8601_DATE_FORMAT,
    handlers=[logging.FileHandler(LOGFILE_NAME), logging.StreamHandler()]
)


class ParallelProcessing:

    def __init__(self: T, cli_args: Dict[str, Union[int, bool, str]]) -> T:

        self.cli_args = cli_args
        self.collection = None

        self.pdb_codes = []
        self.num_codes = 0
        self.count = 0
        self.bool_disable_workers = False

    def get_collection_handle(self: T) -> None:

        uri = f"mongodb://{self.cli_args['host']}:{self.cli_args['port']}/"
        logging.info('Handshaking with MongoDB at "%s"', uri)

        client = MongoClient(uri, serverSelectionTimeoutMS=TIMEOUT_MSEC_MONGODB)

        try:
            client.list_databases()
        except errors.ServerSelectionTimeoutError:
            logging.error('Could not connect to MongoDB')
            sys.exit('Batch job failed')
        except errors.OperationFailure as exception:
            logging.error(exception.details['errmsg'])
            sys.exit('Batch job failed')

        self.collection = client[self.cli_args['database']][self.cli_args['collection']]

    def drop_collection_if_overwrite_enabled(self: T) -> None:

        if not self.cli_args['overwrite']:
            return

        logging.info('Will overwrite collection "%s" if exists', self.cli_args['collection'])
        self.collection.database.drop_collection(self.cli_args['collection'])

        info_collection = f"{self.cli_args['collection']}_info"

        logging.info('Will overwrite collection "%s" if exists', info_collection)
        self.collection.database.drop_collection(info_collection)

    def ensure_collection_does_not_exist(self: T) -> None:

        collections = self.collection.database.list_collection_names()

        if self.cli_args['collection'] in collections:
            logging.error('Collection "%s" exists! Cannot proceed', self.cli_args['collection'])
            sys.exit('Batch job failed')

    def disable_all_workers(self: T, *args) -> None:

        logging.info('Detected SIGINT!')
        logging.info('Attempting to stop all workers!')

        self.bool_disable_workers = True

    def register_ipc_signals(self: T) -> None:

        logging.info('Registering SIGINT to thread terminator')

        self.bool_disable_workers = False
        signal(SIGINT, self.disable_all_workers)

    def get_pdb_code_chunks(self: T) -> None:

        logging.info('Imported pdb codes from file %s', self.cli_args['path_batch_file'])

        with open(self.cli_args['path_batch_file']) as f:
            for line in f:
                for row in split(r'(;|,|\s)\s*', line):
                    if len(row) == LEN_PDB_CODE:
                        self.pdb_codes.append(row)

        self.num_codes = len(self.pdb_codes)

        if self.cli_args['threads'] < 1:
            sys.exit('At least 1 thread required!')

        if self.cli_args['threads'] > 15:
            sys.exit('Maximum number of threads is 15')

        logging.info('Splitting list of pdb codes into %i chunks', self.cli_args['threads'])

        self.pdb_codes = [
            self.pdb_codes[i::self.cli_args['threads']] for i in range(self.cli_args['threads'])
        ]

    def worker_met_aromatic(self: T, chunk: List[str]) -> None:

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
            except Exception:
                self.count += 1
                logging.exception('Could not process code: %s. Count: %i', code, self.count)
            else:
                self.count += 1
                logging.info('Processed %s. Count: %i', code, self.count)
                self.collection.insert_many([results])

    def deploy_jobs(self: T) -> None:

        logging.info('Deploying %i workers!', self.cli_args['threads'])

        batch_job_metadata = {
            'num_workers': self.cli_args['threads'],
            'cutoff_distance': self.cli_args['cutoff_distance'],
            'cutoff_angle': self.cli_args['cutoff_angle'],
            'chain': self.cli_args['chain'],
            'model': self.cli_args['model'],
            'data_acquisition_date': datetime.now()
        }

        name_collection_info = f"{self.cli_args['collection']}_info"
        collection_info = self.collection.database[name_collection_info]

        with futures.ThreadPoolExecutor(max_workers=MAXIMUM_WORKERS) as executor:

            start_time = time()

            workers = [
                executor.submit(self.worker_met_aromatic, chunk) for chunk in self.pdb_codes
            ]

            if futures.wait(workers, return_when=futures.ALL_COMPLETED):
                execution_time = round(time() - start_time, 3)

                logging.info('Batch job complete!')
                logging.info('Results loaded into database: %s', self.cli_args['database'])
                logging.info('Results loaded into collection: %s', self.cli_args['collection'])
                logging.info('Batch job statistics loaded into collection: %s', name_collection_info)
                logging.info('Batch job execution time: %f s', execution_time)

                batch_job_metadata['batch_job_execution_time'] = execution_time
                batch_job_metadata['number_of_entries'] = self.num_codes
                collection_info.insert_one(batch_job_metadata)

    def main(self: T) -> None:

        self.get_collection_handle()

        if self.cli_args['threads'] > MAXIMUM_WORKERS:
            logging.warning('Number of selected workers exceeds maximum number of workers.')
            logging.warning('The thread pool will use a maximum of %i workers.', MAXIMUM_WORKERS)

        self.drop_collection_if_overwrite_enabled()
        self.ensure_collection_does_not_exist()
        self.register_ipc_signals()
        self.get_pdb_code_chunks()

        self.deploy_jobs()
