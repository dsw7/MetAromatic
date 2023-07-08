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
from MetAromatic import consts
from MetAromatic.pair import MetAromatic

LEN_PDB_CODE = 4
MAXIMUM_WORKERS = 15
TIMEOUT_MSEC_MONGODB = 1000


class ParallelProcessing:

    log = logging.getLogger('met-aromatic')

    def __init__(self, cli_args: Dict[str, Union[int, bool, str]]) -> None:

        self.cli_args = cli_args
        self.collection = None

        self.pdb_codes = []
        self.num_codes = 0
        self.count = 0
        self.bool_disable_workers = False

    def set_log_filehandler(self) -> None:

        self.log.debug('Setting up additional logger')

        logfile_name = path.join(gettempdir(), 'met_aromatic.log')
        self.log.info('Will log to file "%s"', logfile_name)

        channel = logging.FileHandler(logfile_name)

        formatter = logging.Formatter(fmt=consts.LOGRECORD_FORMAT, datefmt=consts.ISO_8601_DATE_FORMAT)
        channel.setFormatter(formatter)

        self.log.addHandler(channel)

    def get_collection_handle(self) -> None:

        if self.cli_args['uri'] is None:
            uri = f"mongodb://{self.cli_args['host']}:{self.cli_args['port']}/"
            self.log.info('Handshaking with MongoDB at "%s"', uri)
        else:
            uri = self.cli_args['uri']

        client = MongoClient(uri, serverSelectionTimeoutMS=TIMEOUT_MSEC_MONGODB)

        try:
            client.list_databases()
        except errors.ServerSelectionTimeoutError:
            self.log.error('Could not connect to MongoDB')
            sys.exit('Batch job failed')
        except errors.OperationFailure as exception:
            self.log.error(exception.details['errmsg'])
            sys.exit('Batch job failed')

        self.collection = client[self.cli_args['database']][self.cli_args['collection']]

    def drop_collection_if_overwrite_enabled(self) -> None:

        if not self.cli_args['overwrite']:
            return

        self.log.debug('Will overwrite collection "%s" if exists', self.cli_args['collection'])
        self.collection.database.drop_collection(self.cli_args['collection'])

        info_collection = f"{self.cli_args['collection']}_info"

        self.log.debug('Will overwrite collection "%s" if exists', info_collection)
        self.collection.database.drop_collection(info_collection)

    def ensure_collection_does_not_exist(self) -> None:

        collections = self.collection.database.list_collection_names()

        if self.cli_args['collection'] in collections:
            self.log.error('Collection "%s" exists! Cannot proceed', self.cli_args['collection'])
            sys.exit('Batch job failed')

    def disable_all_workers(self, *args) -> None:

        self.log.info('Detected SIGINT!')
        self.log.info('Attempting to stop all workers!')

        self.bool_disable_workers = True

    def register_ipc_signals(self) -> None:

        self.log.debug('Registering SIGINT to thread terminator')

        self.bool_disable_workers = False
        signal(SIGINT, self.disable_all_workers)

    def get_pdb_code_chunks(self) -> None:

        self.log.info('Imported pdb codes from file %s', self.cli_args['path_batch_file'])

        with open(self.cli_args['path_batch_file']) as f:
            for line in f:
                for row in split(r'(;|,|\s)\s*', line):
                    if len(row) == LEN_PDB_CODE:
                        self.pdb_codes.append(row)

        self.num_codes = len(self.pdb_codes)

        if self.cli_args['threads'] < 1:
            sys.exit('At least 1 thread required!')

        if self.cli_args['threads'] > MAXIMUM_WORKERS:
            sys.exit('Maximum number of threads is 15')

        self.log.debug('Splitting list of pdb codes into %i chunks', self.cli_args['threads'])

        self.pdb_codes = [
            self.pdb_codes[i::self.cli_args['threads']] for i in range(self.cli_args['threads'])
        ]

    def worker_met_aromatic(self, chunk: List[str]) -> None:

        handle_ma = MetAromatic(
            self.cli_args['cutoff_distance'],
            self.cli_args['cutoff_angle'],
            self.cli_args['chain'],
            self.cli_args['model']
        )

        for code in chunk:

            if self.bool_disable_workers:
                self.log.debug('Received interrupt signal - stopping worker thread...')
                break

            try:
                fs = handle_ma.get_met_aromatic_interactions(code)
                results = {
                    '_id': code,
                    'ok': fs.OK,
                    'status': fs.status,
                    'results': fs.interactions
                }
            except Exception:
                self.count += 1
                self.log.exception('Could not process code: %s. Count: %i', code, self.count)
            else:
                self.count += 1
                self.log.info('Processed %s. Count: %i', code, self.count)
                self.collection.insert_one(results)

    def deploy_jobs(self) -> None:

        self.log.debug('Deploying %i workers!', self.cli_args['threads'])

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

        with futures.ThreadPoolExecutor(max_workers=MAXIMUM_WORKERS, thread_name_prefix='Batch') as executor:

            start_time = time()

            workers = [
                executor.submit(self.worker_met_aromatic, chunk) for chunk in self.pdb_codes
            ]

            if futures.wait(workers, return_when=futures.ALL_COMPLETED):
                execution_time = round(time() - start_time, 3)

                self.log.info('Batch job complete!')
                self.log.info('Results loaded into database: %s', self.cli_args['database'])
                self.log.info('Results loaded into collection: %s', self.cli_args['collection'])
                self.log.info('Batch job statistics loaded into collection: %s', name_collection_info)
                self.log.info('Batch job execution time: %f s', execution_time)

                batch_job_metadata['batch_job_execution_time'] = execution_time
                batch_job_metadata['number_of_entries'] = self.num_codes
                collection_info.insert_one(batch_job_metadata)

    def main(self) -> None:

        self.set_log_filehandler()
        self.get_collection_handle()
        self.drop_collection_if_overwrite_enabled()
        self.ensure_collection_does_not_exist()
        self.register_ipc_signals()
        self.get_pdb_code_chunks()
        self.deploy_jobs()
