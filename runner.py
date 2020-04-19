#!/usr/bin/python3
import sys
if sys.version_info[0:2] < (3, 6):
    sys.exit('Minimum required Python version: 3.6\nExiting!')
sys.path.append('src/')


from os import path
from src import frontend
from utilities import pytest_runners


MAX_WORKERS = 15  # put into met_aromatic.conf?

import parallel_processing
import single_processing


def main():
    project_root = path.dirname(path.abspath(__file__))
    cli_args = frontend.get_command_line_arguments()

    if cli_args.ai:
        from src import single_processing
        single_processing.run_single_met_aromatic_query(
            cli_args.code,
            cutoff_distance=cli_args.cutoff_distance,
            cutoff_angle=cli_args.cutoff_angle,
            chain=cli_args.chain,
            model=cli_args.model
        )

    elif cli_args.bi:
        from src import single_processing
        single_processing.run_single_bridging_interaction_query(
            cli_args.code,
            cutoff_distance=cli_args.cutoff_distance,
            cutoff_angle=cli_args.cutoff_angle,
            chain=cli_args.chain,
            model=cli_args.model,
            vertices=cli_args.vertices
        )

    elif cli_args.batch:
        from src import parallel_processing
        parallel_processing.RunBatchJob(
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
