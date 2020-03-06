from argparse import ArgumentParser, RawTextHelpFormatter
from .utilities import help_messages


def get_command_line_arguments():
    parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('--code', help=help_messages.MSG_CODE, type=str, default='1rcy')
    parser.add_argument('--cutoff_distance', help=help_messages.MSG_CUTOFF, default=6.0, type=float)
    parser.add_argument('--cutoff_angle', help=help_messages.MSG_ANGLE, default=109.5, type=float)
    parser.add_argument('--model', help=help_messages.MSG_MODEL, default='cp', type=str)
    parser.add_argument('--chain', help=help_messages.MSG_CHAIN, default='A', type=str)
    parser.add_argument('--query', help=help_messages.MSG_QUERIES, default='ai', type=str)
    parser.add_argument('--vertices', help=help_messages.MSG_VERTICES, default=3, type=int)
    parser.add_argument('--test', help=help_messages.MSG_TEST, action='store_true')
    parser.add_argument('--testcov', help=help_messages.MSG_TEST_COV, action='store_true')
    return parser.parse_args()
