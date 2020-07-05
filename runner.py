#!/usr/bin/env python3

import sys
from os import path

MINIMUM_VERSION_PY = (3, 6)
PROJECT_ROOT = path.dirname(path.abspath(__file__))
EXIT_FAILURE = 1

if sys.version_info[0:2] < MINIMUM_VERSION_PY:
    print('Minimum required Python version: %s.%s\nExiting!' % MINIMUM_VERSION_PY)
    sys.exit(EXIT_FAILURE)
else:
    sys.path.append(path.join(PROJECT_ROOT, 'src/'))

from frontend import get_command_line_arguments
from utilities.logger import print_error
from single_processing import RunSingleQuery


def main():
    # Import runners in main function on an as-needed basis - don't force users
    # to import everything just to run --help...

    command_line_args = get_command_line_arguments()

    if command_line_args.single_aromatic_interaction_query:
        RunSingleQuery(command_line_args).single_met_aromatic_query()

    elif command_line_args.single_bridging_interaction_query: 
        RunSingleQuery(command_line_args).single_bridging_interaction_query()

    elif command_line_args.run_batch_job:
        from parallel_processing import BatchJobOrchestrator
        BatchJobOrchestrator(
            batch_file=command_line_args.run_batch_job,
            num_workers=command_line_args.threads,
            cutoff_distance=command_line_args.cutoff_distance,
            cutoff_angle=command_line_args.cutoff_angle,
            chain=command_line_args.chain,
            model=command_line_args.model,
            database=command_line_args.database,
            collection=command_line_args.collection,
            host=command_line_args.host,
            port=command_line_args.port
        ).deploy_jobs()

    elif command_line_args.run_tests:
        from testing import TestRunner
        TestRunner(
            PROJECT_ROOT,
            expression=command_line_args.test_expression,
            exit_on_failure=command_line_args.exit_on_failure,
            verbose=(not command_line_args.quiet)
        ).run_tests()

    elif command_line_args.run_tests_with_coverage:
        from testing import TestRunner
        TestRunner(
            PROJECT_ROOT,
            expression=command_line_args.test_expression,
            exit_on_failure=command_line_args.exit_on_failure,
            verbose=(not command_line_args.quiet)
        ).run_tests_with_coverage()

if __name__ == '__main__':
    main()
