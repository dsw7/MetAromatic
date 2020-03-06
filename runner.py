import sys
from os import path

if sys.version_info[0:2] < (3, 6):
    sys.exit('Minimum required Python version: 3.6\nExiting!')

from src import (
    met_aromatic,
    frontend
)

from src.utilities import (
    pytest_runners,
    formatter,
    errors
)

ROOT = path.dirname(path.abspath(__file__))


def main():
    cli_args = frontend.get_command_line_arguments()

    if cli_args.test:
        sys.exit(pytest_runners.run_tests(ROOT))

    if cli_args.testcov:
        sys.exit(pytest_runners.run_tests_with_coverage(ROOT))

    ma = met_aromatic.MetAromatic(
        cli_args.code,
        cutoff_distance=cli_args.cutoff_distance,
        cutoff_angle=cli_args.cutoff_angle,
        chain=cli_args.chain,
        model=cli_args.model
    )

    if cli_args.query == 'ai':
        results = ma.get_met_aromatic_interactions()
    elif cli_args.query == 'bi':
        results = ma.get_bridging_interactions(number_vertices=cli_args.vertices)
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
