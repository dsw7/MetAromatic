import sys
from met_aromatic import MetAromatic
from utilities.formatter import custom_pretty_print_single_bridging_interaction


HEADER = ['ARO', 'POS', 'MET POS', 'NORM', 'MET-THETA', 'MET-PHI']


def run_single_met_aromatic_query(code, cutoff_distance, cutoff_angle, chain, model):
    results = MetAromatic(
        code,
        cutoff_distance=cutoff_distance,
        cutoff_angle=cutoff_angle,
        chain=chain,
        model=model
    ).get_met_aromatic_interactions()


    if results['exit_code'] == 0:
        print("{:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(*HEADER))
        for line in results['results']:
            print("{:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(*line.values()))


def run_single_bridging_interaction_query(code, cutoff_distance,
                                          cutoff_angle, chain,
                                          model, vertices):
    results = MetAromatic(
        code,
        cutoff_distance=cutoff_distance,
        cutoff_angle=cutoff_angle,
        chain=chain,
        model=model
    ).get_bridging_interactions(number_vertices=vertices)

    if not isinstance(results, list):
        sys.exit(results)

    custom_pretty_print_single_bridging_interaction(results)
