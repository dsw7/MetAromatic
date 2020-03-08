#!/usr/bin/python3
import sys
if sys.version_info[0:2] < (3, 6):
    sys.exit('Minimum required Python version: 3.6\nExiting!')
from os import path
from itertools import chain as itertools_chain
from concurrent import futures
from pymongo import MongoClient
from numpy import array_split
from src import (
    met_aromatic,
    frontend
)
from src.utilities import (
    pytest_runners,
    formatter,
    errors
)


def run_single_met_aromatic_query(code, cutoff_distance, cutoff_angle, chain, model):
    results = met_aromatic.MetAromatic(
        code,
        cutoff_distance=cutoff_distance,
        cutoff_angle=cutoff_angle,
        chain=chain,
        model=model
    ).get_met_aromatic_interactions()

    if not isinstance(results, list):
        if issubclass(results, errors.InvalidCutoffsError):
            sys.exit(errors.ErrorCodes.InvalidCutoffs)
        elif issubclass(results, errors.InvalidPDBFileError):
            sys.exit(errors.ErrorCodes.InvalidPDBFile)
        elif issubclass(results, errors.NoMetCoordinatesError):
            sys.exit(errors.ErrorCodes.NoMetCoordinates)
        elif issubclass(results, errors.NoAromaticCoordinatesError):
            sys.exit(errors.ErrorCodes.NoAromaticCoordinates)
        elif issubclass(results, errors.InvalidModelError):
            sys.exit(errors.ErrorCodes.InvalidModel)
        elif issubclass(results, errors.NoResultsError):
            sys.exit(errors.ErrorCodes.NoResults)

    formatter.custom_pretty_print(results)


def run_single_bridging_interaction_query(code, cutoff_distance, cutoff_angle, chain, model, vertices):
    results = met_aromatic.MetAromatic(
        code,
        cutoff_distance=cutoff_distance,
        cutoff_angle=cutoff_angle,
        chain=chain,
        model=model
    ).get_bridging_interactions(number_vertices=vertices)

    if not isinstance(results, list):
        if issubclass(results, errors.InvalidCutoffsError):
            sys.exit(errors.ErrorCodes.InvalidCutoffs)
        elif issubclass(results, errors.InvalidPDBFileError):
            sys.exit(errors.ErrorCodes.InvalidPDBFile)
        elif issubclass(results, errors.NoMetCoordinatesError):
            sys.exit(errors.ErrorCodes.NoMetCoordinates)
        elif issubclass(results, errors.NoAromaticCoordinatesError):
            sys.exit(errors.ErrorCodes.NoAromaticCoordinates)
        elif issubclass(results, errors.InvalidModelError):
            sys.exit(errors.ErrorCodes.InvalidModel)
        elif issubclass(results, errors.NoResultsError):
            sys.exit(errors.ErrorCodes.NoResults)
        elif issubclass(results, errors.BadVerticesError):
            sys.exit(errors.ErrorCodes.BadVerticesError)

    formatter.custom_pretty_print(results)


class RunBatchJob:
    def __init__(
            self, batch_file, num_threads,
            cutoff_distance, cutoff_angle, chain,
            model, host, port, database, collection
        ):
        self.batch_file = batch_file
        self.num_threads = num_threads
        self.cutoff_distance = cutoff_distance
        self.cutoff_angle = cutoff_angle
        self.chain = chain
        self.model = model
        self.collection = MongoClient(host, port)[database][collection]

    def open_batch_file(self):
        try:
            with open(self.batch_file) as f:
                data = [line.split(', ') for line in f]
        except FileNotFoundError:
            sys.exit(errors.ErrorCodes.MissingFile)
        else:
            return list(itertools_chain(*data))

    def met_aromatic_thread(self, list_codes):
        for code in list_codes:
            results = met_aromatic.MetAromatic(
                code=code,
                cutoff_distance=self.cutoff_distance,
                cutoff_angle=self.cutoff_angle,
                chain=self.chain,
                model=self.model
            ).get_met_aromatic_interactions_mongodb_output()

            if isinstance(results, dict):
                self.collection.insert(results)

    def run_batch_job(self):
        pdb_codes = self.open_batch_file()
        if not pdb_codes:
            return None    # TODO: create custom exception

        batch_pdb_codes = array_split(pdb_codes, self.num_threads)
        future = [None] * self.num_threads
        with futures.ThreadPoolExecutor() as executor:
            for index in range(0, self.num_threads):
                future[index] = executor.submit(self.met_aromatic_thread, batch_pdb_codes[index])

        for index in range(0, self.num_threads):
            exit_status = future[index].result()
            if exit_status:
                print(exit_status)


def main():
    project_root = path.dirname(path.abspath(__file__))
    cli_args = frontend.get_command_line_arguments()

    if cli_args.ai:
        run_single_met_aromatic_query(
            cli_args.code, cutoff_distance=cli_args.cutoff_distance,
            cutoff_angle=cli_args.cutoff_angle, chain=cli_args.chain,
            model=cli_args.model
        )
    elif cli_args.bi:
        run_single_bridging_interaction_query(
            cli_args.code, cutoff_distance=cli_args.cutoff_distance,
            cutoff_angle=cli_args.cutoff_angle, chain=cli_args.chain,
            model=cli_args.model, vertices=cli_args.vertices
        )
    elif cli_args.batch:
        print('batch')
    elif cli_args.test:
        pytest_runners.run_tests(project_root)
    elif cli_args.testcov:
        pytest_runners.run_tests_with_coverage(project_root)


if __name__ == '__main__':
    main()
