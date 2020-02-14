import sys
from os import path
from argparse import ArgumentParser, RawTextHelpFormatter
from pytest import main as pytest_main
from src import met_aromatic
from src.utilities import (
    help_messages,
    formatter,
    errors
)


ROOT = path.dirname(path.abspath(__file__))


def run_tests(root):
    return pytest_main(f'{root} -vs'.split())


def run_tests_with_coverage(root):
    return pytest_main([
        f'{root}',
        '-vs',
        f'--cov={root}',
        f'--cov-report=html:{root}/htmlcov',
        f'--cov-config={root}/.coveragerc'
    ])


def main():
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

    code = parser.parse_args().code
    cutoff_distance = parser.parse_args().cutoff_distance
    cutoff_angle = parser.parse_args().cutoff_angle
    model = parser.parse_args().model
    chain = parser.parse_args().chain
    query = parser.parse_args().query
    vertices = parser.parse_args().vertices
    run_tests_bool = parser.parse_args().test
    run_tests_coverage_bool = parser.parse_args().testcov

    if run_tests_bool:
        sys.exit(run_tests(ROOT))

    if run_tests_coverage_bool:
        sys.exit(run_tests_with_coverage(ROOT))

    ma = met_aromatic.MetAromatic(
        code,
        cutoff_distance=cutoff_distance,
        cutoff_angle=cutoff_angle,
        chain=chain,
        model=model
    )

    if query == 'ai':
        results = ma.get_met_aromatic_interactions()
    elif query == 'bi':
        results = ma.get_bridging_interactions(number_vertices=vertices)
    else:
        sys.exit(errors.ErrorCodes.BadQueryType)

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


if __name__ == '__main__':
    main()
