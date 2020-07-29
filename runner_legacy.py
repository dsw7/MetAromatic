#!/usr/bin/env python3

import sys
from os import path

MINIMUM_VERSION_PY = (3, 6)
EXIT_FAILURE = 1
PROJECT_ROOT = path.dirname(path.abspath(__file__))

if sys.version_info[0:2] < MINIMUM_VERSION_PY:
    print('Minimum required Python version: %s.%s\nExiting!' % MINIMUM_VERSION_PY)
    sys.exit(EXIT_FAILURE)
else:
    sys.path.append(path.join(PROJECT_ROOT, 'src/'))

from frontend import get_command_line_arguments
from single_processing import RunSingleQuery
from parallel_processing import RunBatchQueries
from testing import RunTests

def main():
    command_line_args = get_command_line_arguments()

    if command_line_args.single_aromatic_interaction_query:
        RunSingleQuery(command_line_args).single_met_aromatic_query()

    elif command_line_args.single_bridging_interaction_query:
        RunSingleQuery(command_line_args).single_bridging_interaction_query()

    elif command_line_args.run_batch_job:
        RunBatchQueries(command_line_args).deploy_jobs()

    elif command_line_args.run_tests:
        RunTests(command_line_args, PROJECT_ROOT).run_tests()

    elif command_line_args.run_tests_with_coverage:
        RunTests(command_line_args, PROJECT_ROOT).run_tests_with_coverage()

if __name__ == '__main__':
    main()
