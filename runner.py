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
    from utilities.check_network import check_network_connection


def main():
    # Import runners in main function on an as-needed basis - don't force users
    # to import everything just to run --help...

    check_network_connection()
    command_line_args = get_command_line_arguments()

    if command_line_args.single_aromatic_interaction_query:
        from single_processing import run_single_met_aromatic_query
        run_single_met_aromatic_query(
            command_line_args.single_aromatic_interaction_query,
            cutoff_distance=command_line_args.cutoff_distance,
            cutoff_angle=command_line_args.cutoff_angle,
            chain=command_line_args.chain,
            model=command_line_args.model
        )

    elif command_line_args.single_bridging_interaction_query:
        from single_processing import run_single_bridging_interaction_query
        run_single_bridging_interaction_query(
            command_line_args.single_bridging_interaction_query,
            cutoff_distance=command_line_args.cutoff_distance,
            cutoff_angle=command_line_args.cutoff_angle,
            chain=command_line_args.chain,
            model=command_line_args.model,
            vertices=command_line_args.vertices
        )

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
