import sys
import logging
from re import split
from time import time
from datetime import datetime
from concurrent import futures
from pymongo import MongoClient
from numpy import array_split
from met_aromatic import MetAromatic
from utilities.errors import ErrorCodes


MAX_WORKERS = 15  # put into met_aromatic.conf?
EXIT_FAILURE = 1
EXIT_SUCCESS = 0


class Logging:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s:%(asctime)s: -> %(message)s',
            datefmt='%d-%b-%y %H:%M:%S',
            handlers=[
                logging.FileHandler('file.log'),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger()

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)


class BatchJobOrchestrator:
    def __init__(self, batch_file, num_workers,
                 cutoff_distance, cutoff_angle, chain,
                 model, host, port, database, collection):

        self.batch_file = batch_file
        self.num_workers = num_workers
        self.cutoff_distance = cutoff_distance
        self.cutoff_angle = cutoff_angle
        self.chain = chain
        self.model = model
        self.client = MongoClient(host, port)
        self.collection_name = collection
        self.database_name = database
        self.logger = Logging()

        if self.num_workers > MAX_WORKERS:
            self.logger.warning('Number of selected workers exceeds maximum number of workers.')
            self.logger.warning(f'The thread pool will use a maximum of {MAX_WORKERS} workers.')

    def open_batch_file(self):
        if not self.batch_file:
            self.logger.error('The --batch </path/to/file> parameter was not provided.')
            sys.exit(EXIT_FAILURE)
        try:
            data = []
            with open(self.batch_file) as batch:
                for line in batch:
                    data.extend([i for i in split(r'(;|,|\s)\s*', line) if len(i) == 4])
        except FileNotFoundError:
            self.logger.error('Invalid batch file!')
            sys.exit(ErrorCodes.MissingFileError)
        else:
            return data

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
            except Exception as exception:
                # catch remaining unhandled exceptions
                collection_results.insert(
                    {
                        '_id': code,
                        'exit_code': ErrorCodes.OtherError,
                        'exit_status': repr(exception),
                        'results': None
                    }
                )
            else:
                self.logger.info(f'Processed {code}')
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
            sys.exit(ErrorCodes.BadDatabaseCollectionError)

        pdb_codes = self.open_batch_file()
        chunked_pdb_codes = array_split(pdb_codes, self.num_workers)

        name_collection_info = f'{self.collection_name}_info'
        collection_info = self.client[self.database_name][name_collection_info]

        self.logger.info(f'Deploying {self.num_workers} workers!')

        with futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            start_time = time()
            workers = [
                executor.submit(self.worker, chunk) for chunk in chunked_pdb_codes
            ]

            if futures.wait(workers, return_when=futures.ALL_COMPLETED):
                self.logger.info('Batch job complete!')
                self.logger.info('MongoDB destination:')
                self.logger.info(f'Database:       {self.database_name}')
                self.logger.info(f'Collection:     {self.collection_name}')
                self.logger.info(f'Job statistics: {name_collection_info}')

                collection_info.insert(
                    self.prepare_batch_job_info(
                        time() - start_time,
                        len(pdb_codes)
                    )
                )
