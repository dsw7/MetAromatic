from numpy.linalg import norm
from utilities.math_utils.cross_product_method import vector_angle

def apply_distance_angular_condition(midpoints, lone_pairs, cutoff_distance, cutoff_angle):
    pairs = []    
    for dict_met in lone_pairs:
        for midpoint in midpoints:
            vector_v = midpoint[2] - dict_met['coords_sd']
            norm_v = norm(vector_v)
            if norm_v <= cutoff_distance:  # distance condition
                met_theta = vector_angle(vector_v, dict_met['vector_a'])
                met_phi = vector_angle(vector_v, dict_met['vector_g'])
                if (met_theta <= cutoff_angle) or (met_phi <= cutoff_angle):  # angular condition
                    pairs.append([midpoint[1], midpoint[0], 'MET', dict_met['position'], norm_v, met_theta, met_phi])
                else:
                    pass
            else:
                pass
    return pairs
