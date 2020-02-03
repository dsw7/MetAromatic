from itertools import groupby
from operator import itemgetter
from numpy import array
from utilities.math_utils.rodrigues_method import RodriguesMethod
from utilities.math_utils.cross_product_method import CrossProductMethod


def preprocess_met_data(methionine_coords):
    processed_met_data = []
    for _, met_grouped in groupby(methionine_coords, lambda entry: entry[5]):
        met_ordered = sorted(list(met_grouped), key=itemgetter(2))
        dict_met = {}
        dict_met['coords_ce'] = array(met_ordered[0][6:9]).astype(float)
        dict_met['coords_cg'] = array(met_ordered[1][6:9]).astype(float)
        dict_met['coords_sd'] = array(met_ordered[2][6:9]).astype(float)
        dict_met['position'] = met_ordered[0][5]
        processed_met_data.append(dict_met)
    return processed_met_data


def get_lone_pairs(methionine_coords, model):
    processed_met_data = preprocess_met_data(methionine_coords)
    lone_pairs = []
    for dict_met in processed_met_data:
        dict_lone_pairs = {}
        coords_cg = dict_met['coords_cg']
        coords_ce = dict_met['coords_ce']
        coords_sd = dict_met['coords_sd']

        if model == 'rm':
            object_lonepairs = RodriguesMethod(coords_cg, coords_sd, coords_ce)
        elif model == 'cp':
            object_lonepairs = CrossProductMethod(coords_cg, coords_sd, coords_ce)
        else:
            return False

        dict_lone_pairs['vector_a'] = object_lonepairs.get_vector_a()
        dict_lone_pairs['vector_g'] = object_lonepairs.get_vector_g()
        dict_lone_pairs['coords_sd'] = dict_met['coords_sd']
        dict_lone_pairs['position'] = dict_met['position']
        lone_pairs.append(dict_lone_pairs)
    return lone_pairs
