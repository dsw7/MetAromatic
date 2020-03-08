import sys
from os import path
from argparse import ArgumentParser, RawTextHelpFormatter
from yaml import safe_load
from .utilities import (
    help_messages,
    errors
)


def get_defaults():
    root = path.dirname(path.abspath(__file__))
    try:
        with open(path.join(root, 'met_aromatic.conf')) as conf_file:
            constants = safe_load(conf_file)
    except FileNotFoundError:
        sys.exit(errors.ErrorCodes.MissingFile)
    else:
        return constants


def get_command_line_arguments():
    constants = get_defaults()
    parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
    job_type = parser.add_mutually_exclusive_group()
    job_type.add_argument('--ai', help=help_messages.MSG_AI, action='store_true')
    job_type.add_argument('--bi', help=help_messages.MSG_BI, action='store_true')
    job_type.add_argument('--batch', help=help_messages.MSG_BATCH, action='store_true')
    job_type.add_argument('--test', help=help_messages.MSG_TEST, action='store_true')
    job_type.add_argument('--testcov', help=help_messages.MSG_TEST_COV, action='store_true')

    parser.add_argument(
        '--code',
        help=help_messages.MSG_CODE,
        type=str, default=constants['default_pdb_code']
    )

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

    return parser.parse_args()
