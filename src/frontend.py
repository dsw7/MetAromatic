import sys
from os import path
from argparse import ArgumentParser, RawTextHelpFormatter
from yaml import safe_load
from utilities import (
    help_messages,
    errors
)


def get_defaults():
    root = path.dirname(path.abspath(__file__))
    try:
        with open(path.join(root, 'met_aromatic.conf')) as conf_file:
            constants = safe_load(conf_file)
    except FileNotFoundError:
        sys.exit(errors.ErrorCodes.MissingFileError)
    else:
        return constants


def get_command_line_arguments():
    constants = get_defaults()
    parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
    job_type = parser.add_mutually_exclusive_group()
    job_type.add_argument('--ai', help=help_messages.MSG_AI, dest='single_aromatic_interaction_query')
    job_type.add_argument('--bi', help=help_messages.MSG_BI, dest='single_bridging_interaction_query')
    job_type.add_argument('--batch', help=help_messages.MSG_BATCH, dest='run_batch_job')
    job_type.add_argument('--test', help=help_messages.MSG_TEST, action='store_true', dest='run_tests')
    job_type.add_argument('--testcov', help=help_messages.MSG_TEST_COV, action='store_true', dest='run_tests_with_coverage')

    parser.add_argument(
        '--cutoff_distance',
        help=help_messages.MSG_CUTOFF,
        default=constants['default_cutoff_distance'],
        type=float
    )

    parser.add_argument(
        '--cutoff_angle',
        help=help_messages.MSG_ANGLE,
        default=constants['default_cutoff_angle'],
        type=float
    )

    parser.add_argument(
        '--model',
        help=help_messages.MSG_MODEL,
        default=constants['default_model'],
        type=str
    )

    parser.add_argument(
        '--chain',
        help=help_messages.MSG_CHAIN,
        default=constants['default_chain'],
        type=str
    )

    parser.add_argument(
        '--vertices',
        help=help_messages.MSG_VERTICES,
        default=constants['default_vertices'],
        type=int
    )

    parser.add_argument(
        '--host',
        help=help_messages.MSG_HOST,
        default=constants['default_mongodb_host']
    )

    parser.add_argument(
        '--port',
        help=help_messages.MSG_PORT,
        default=constants['default_mongodb_port'],
        type=int
    )

    parser.add_argument(
        '--database',
        help=help_messages.MSG_DB,
        default=constants['default_mongodb_database']
    )

    parser.add_argument(
        '--collection',
        help=help_messages.MSG_COL,
        default=constants['default_mongodb_collection']
    )

    parser.add_argument(
        '--threads',
        help=help_messages.MSG_THREADS,
        default=constants['default_threads'],
        type=int
    )

    parser.add_argument(
        '--test-expression',
        help=help_messages.MSG_TEST_EXPRESSION,
        dest='test_expression'
    )

    parser.add_argument(
        '--exit-on-failure',
        action='store_true',
        help=help_messages.MSG_EXIT_ON_FAILURE,
        dest='exit_on_failure'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        default=False,
        help=help_messages.MSG_QUIET
    )

    return parser.parse_args()
