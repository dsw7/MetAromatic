import sys
from src.met_aromatic import MetAromatic
from src.utilities import formatter


def run_single_met_aromatic_query(code, cutoff_distance, cutoff_angle, chain, model):
    results = MetAromatic(
        code,
        cutoff_distance=cutoff_distance,
        cutoff_angle=cutoff_angle,
        chain=chain,
        model=model
    ).get_met_aromatic_interactions()

    if not isinstance(results, list):
        sys.exit(results)

    formatter.custom_pretty_print_single_aromatic_interaction(results)


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

    formatter.custom_pretty_print_single_bridging_interaction(results)
