#!/usr/bin/env python3
import sys
if sys.version_info[0:2] < (3, 6):
    sys.exit('Minimum required Python version: 3.6\nExiting!')
sys.path.append('src/')
from os import path
from frontend import get_command_line_arguments


def main():
    project_root = path.dirname(path.abspath(__file__))
    cli_args = get_command_line_arguments()

    if cli_args.ai:
        from single_processing import run_single_met_aromatic_query
        run_single_met_aromatic_query(
            cli_args.code,
            cutoff_distance=cli_args.cutoff_distance,
            cutoff_angle=cli_args.cutoff_angle,
            chain=cli_args.chain,
            model=cli_args.model
        )

    elif cli_args.bi:
        from single_processing import run_single_bridging_interaction_query
        run_single_bridging_interaction_query(
            cli_args.code,
            cutoff_distance=cli_args.cutoff_distance,
            cutoff_angle=cli_args.cutoff_angle,
            chain=cli_args.chain,
            model=cli_args.model,
            vertices=cli_args.vertices
        )

    elif cli_args.batch:
        from parallel_processing import RunBatchJob
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
        from utilities.pytest_runners import run_tests
        run_tests(project_root)

    elif cli_args.testcov:
        from utilities.pytest_runners import run_tests_with_coverage
        run_tests_with_coverage(project_root)


if __name__ == '__main__':
    main()
