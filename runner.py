import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from src import met_aromatic
from src.utilities import help_messages
from src.utilities import formatter
from src.utilities import errors


def main():
    parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('--code', help=help_messages.MSG_CODE, type=str, required=True)
    parser.add_argument('--cutoff_distance', help=help_messages.MSG_CUTOFF, default=6.0, type=float)
    parser.add_argument('--cutoff_angle', help=help_messages.MSG_ANGLE, default=109.5, type=float)
    parser.add_argument('--model', help=help_messages.MSG_MODEL, default='cp', type=str)
    parser.add_argument('--chain', help=help_messages.MSG_CHAIN, default='A', type=str)
    parser.add_argument('--query', help=help_messages.MSG_QUERIES, default='ai', type=str)
    parser.add_argument('--vertices', help=help_messages.MSG_VERTICES, default=3, type=int)

    code = parser.parse_args().code
    cutoff_distance = parser.parse_args().cutoff_distance
    cutoff_angle = parser.parse_args().cutoff_angle
    model = parser.parse_args().model
    chain = parser.parse_args().chain
    query = parser.parse_args().query
    vertices = parser.parse_args().vertices

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
