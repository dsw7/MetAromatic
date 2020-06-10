import sys
from met_aromatic import MetAromatic
from utilities.logger import print_error

HEADER_SUCCESS = ['ARO', 'POS', 'MET POS', 'NORM', 'MET-THETA', 'MET-PHI']
HEADER_FAILURE = ['EXIT CODE', 'EXIT STATUS']


def run_single_met_aromatic_query(code, cutoff_distance, cutoff_angle, chain, model):
    results = MetAromatic(
        code, cutoff_distance=cutoff_distance, cutoff_angle=cutoff_angle,
        chain=chain, model=model
    ).get_met_aromatic_interactions()

    if results['exit_code'] == 0:
        print("{:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(*HEADER_SUCCESS))
        for line in results['results']:
            print("{:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(*line.values()))
    else:
        print_error(results['exit_status'])
        print_error(f"Exited with code: {results['exit_code']}")

    sys.exit(results['exit_code'])


def run_single_bridging_interaction_query(code, cutoff_distance, cutoff_angle, chain, model, vertices):
    results = MetAromatic(
        code, cutoff_distance=cutoff_distance, cutoff_angle=cutoff_angle,
        chain=chain, model=model
    ).get_bridging_interactions(number_vertices=vertices)

    if results['exit_code'] == 0:
        print(results['results'])
    else:
        print_error(results['exit_status'])
        print_error(f"Exited with code: {results['exit_code']}")

    sys.exit(results['exit_code'])
