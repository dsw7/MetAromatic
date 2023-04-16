from itertools import groupby
from operator import itemgetter
from numpy import array
from core.helpers.lone_pair_interpolators import RodriguesMethod, CrossProductMethod

def get_lone_pairs(met_coordinates: list, model: str) -> list:

    lone_pairs = []

    for position, groups in groupby(met_coordinates, lambda entry: entry[5]):
        ordered = sorted(list(groups), key=itemgetter(2))

        coordinates_ce = array(ordered[0][6:9]).astype(float)
        coordinates_cg = array(ordered[1][6:9]).astype(float)
        coordinates_sd = array(ordered[2][6:9]).astype(float)

        if model == 'cp':
            lonepair = CrossProductMethod(coordinates_cg, coordinates_sd, coordinates_ce)
        else:
            lonepair = RodriguesMethod(coordinates_cg, coordinates_sd, coordinates_ce)

        lone_pairs.append({
            'vector_a': lonepair.get_vector_a(),
            'vector_g': lonepair.get_vector_g(),
            'coords_sd': coordinates_sd,
            'position': position
        })

    return lone_pairs
