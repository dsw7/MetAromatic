#!/usr/bin/python3
import sys
from os import path
from re import split
from time import time
from datetime import datetime
from concurrent import futures
from pymongo import MongoClient
from numpy import array_split
from tqdm import tqdm

if sys.version_info[0:2] < (3, 6):
    sys.exit('Minimum required Python version: 3.6\nExiting!')

from src import (
    met_aromatic,
    frontend
)
from src.utilities import (
    pytest_runners,
    formatter,
    errors
)


MAX_WORKERS = 15  # put into met_aromatic.conf?


def run_single_met_aromatic_query(code, cutoff_distance, cutoff_angle, chain, model):
    results = met_aromatic.MetAromatic(
        code,
        cutoff_distance=cutoff_distance,
        cutoff_angle=cutoff_angle,
        chain=chain,
        model=model
    ).get_met_aromatic_interactions()

    if not isinstance(results, list):
        sys.exit(results)

    formatter.custom_pretty_print_single_aromatic_interaction(results)


def run_single_bridging_interaction_query(code, cutoff_distance,
                                          cutoff_angle, chain,
                                          model, vertices):
    results = met_aromatic.MetAromatic(
        code,
        cutoff_distance=cutoff_distance,
        cutoff_angle=cutoff_angle,
        chain=chain,
        model=model
    ).get_bridging_interactions(number_vertices=vertices)

    if not isinstance(results, list):
        sys.exit(results)

    formatter.custom_pretty_print_single_bridging_interaction(results)


class RunBatchJob:
    def __init__(self, batch_file, num_workers,
                 cutoff_distance, cutoff_angle, chain,
                 model, host, port, database, collection):
        self.batch_file = batch_file
        self.num_workers = num_workers
        self.cutoff_distance = cutoff_distance
        self.cutoff_angle = cutoff_angle
        self.chain = chain
        self.model = model
        self.collection_results = MongoClient(host, port)[database][collection]
        self.collection_info = MongoClient(host, port)[database][f'{collection}_info']


    def open_batch_file(self):
        if not self.batch_file:
            sys.exit('The --batch_file </path/to/file> parameter was not provided.')

        try:
            data = []
            with open(self.batch_file) as batch:
                for line in batch:
                    data.extend([i for i in split(r'(;|,|\s)\s*', line) if len(i) == 4])
        except FileNotFoundError:
            print('Invalid batch file!')
            sys.exit(errors.ErrorCodes.MissingFileError)
        else:
            return data


    def worker(self, list_codes):
        for code in tqdm(list_codes):
            try:
                results = met_aromatic.MetAromatic(
                    code=code,
                    cutoff_distance=self.cutoff_distance,
                    cutoff_angle=self.cutoff_angle,
                    chain=self.chain,
                    model=self.model
                ).get_met_aromatic_interactions_mongodb_output()
            except Exception as exception:
                # catch remaining unhandled exceptions
                self.collection_results.insert({'code': code, 'exception': repr(exception)})
            else:
                self.collection_results.insert(results)


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


    def run_batch_job_threadpoolexecutor(self):
        pdb_codes = self.open_batch_file()
        chunked_pdb_codes = array_split(pdb_codes, self.num_workers)

        with futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            start_time = time()
            workers = [
                executor.submit(self.worker, chunk) for chunk in chunked_pdb_codes
            ]

            if futures.wait(workers, return_when=futures.ALL_COMPLETED):
                self.collection_info.insert(
                    self.prepare_batch_job_info(
                        time() - start_time,
                        len(pdb_codes)
                    )
                )


def main():
    project_root = path.dirname(path.abspath(__file__))
    cli_args = frontend.get_command_line_arguments()

    if cli_args.ai:
        run_single_met_aromatic_query(
            cli_args.code,
            cutoff_distance=cli_args.cutoff_distance,
            cutoff_angle=cli_args.cutoff_angle,
            chain=cli_args.chain,
            model=cli_args.model
        )

    elif cli_args.bi:
        run_single_bridging_interaction_query(
            cli_args.code,
            cutoff_distance=cli_args.cutoff_distance,
            cutoff_angle=cli_args.cutoff_angle,
            chain=cli_args.chain,
            model=cli_args.model,
            vertices=cli_args.vertices
        )

    elif cli_args.batch:
        RunBatchJob(
            batch_file=cli_args.batch_file,
            num_workers=cli_args.threads,
            cutoff_distance=cli_args.cutoff_distance,
            cutoff_angle=cli_args.cutoff_angle,
            chain=cli_args.chain,
            model=cli_args.model,
            database=cli_args.database,
            collection=cli_args.collection,
            host=cli_args.host,
            port=cli_args.port
        ).run_batch_job_threadpoolexecutor()

    elif cli_args.test:
        pytest_runners.run_tests(project_root)

    elif cli_args.testcov:
        pytest_runners.run_tests_with_coverage(project_root)


if __name__ == '__main__':
    main()
