import sys
from re import split
from time import time
from datetime import datetime
from concurrent import futures
from pymongo import MongoClient
from numpy import array_split
from tqdm import tqdm
from colorama import Fore, Style
from met_aromatic import MetAromatic
from utilities.errors import ErrorCodes


MAX_WORKERS = 15  # put into met_aromatic.conf?


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

        if self.num_workers > MAX_WORKERS:
            print(Fore.YELLOW)
            print('Number of selected workers exceeds maximum number of workers.')
            print(f'The thread pool will use a maximum of {MAX_WORKERS} workers.')
            print(Style.RESET_ALL)

    def open_batch_file(self):
        if not self.batch_file:
            sys.exit('The --batch_file </path/to/file> parameter was not provided.')
        try:
            data = []
            with open(self.batch_file) as batch:
                for line in batch:
                    data.extend([i for i in split(r'(;|,|\s)\s*', line) if len(i) == 4])
        except FileNotFoundError:
            print(Fore.RED + 'Invalid batch file!' + Style.RESET_ALL)
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

        for code in tqdm(list_codes):
            try:
                results = MetAromatic(
                    code=code,
                    cutoff_distance=self.cutoff_distance,
                    cutoff_angle=self.cutoff_angle,
                    chain=self.chain,
                    model=self.model
                ).get_met_aromatic_interactions_mongodb_output()
            except Exception as exception:
                # catch remaining unhandled exceptions
                collection_results.insert(
                    {'_id': code, 'exception': True, 'exception_type': repr(exception)}
                )
            else:
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
            print((
                f'{Fore.RED}'
                f'Database/collection pair '
                f'{self.database_name}.{self.collection_name} exists. '
                f'Use a different collection name. '
                f'Exiting. {Style.RESET_ALL}'
            ))
            sys.exit(ErrorCodes.BadDatabaseCollectionError)

        pdb_codes = self.open_batch_file()
        chunked_pdb_codes = array_split(pdb_codes, self.num_workers)

        name_collection_info = f'{self.collection_name}_info'
        collection_info = self.client[self.database_name][name_collection_info]

        with futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            print(Fore.GREEN + f'Deploying {self.num_workers} workers!\n' + Style.RESET_ALL)

            start_time = time()
            workers = [
                executor.submit(self.worker, chunk) for chunk in chunked_pdb_codes
            ]

            if futures.wait(workers, return_when=futures.ALL_COMPLETED):
                print(Fore.GREEN)
                print('Batch job complete!\nMongoDB destination: ')
                print(f'> Database:       {self.database_name}')
                print(f'> Collection:     {self.collection_name}')
                print(f'> Job statistics: {name_collection_info}')
                print(Style.RESET_ALL)

                collection_info.insert(
                    self.prepare_batch_job_info(
                        time() - start_time,
                        len(pdb_codes)
                    )
                )
