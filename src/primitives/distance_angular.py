from numpy.linalg import norm
from .math_utils.cross_product_method import vector_angle

ROUND_TO_NUMBER = 3

def apply_distance_angular_condition(midpoints, lone_pairs, cutoff_distance, cutoff_angle):
    results = []
    for dict_met in lone_pairs:
        for midpoint in midpoints:
            vector_v = midpoint[2] - dict_met['coords_sd']
            norm_v = norm(vector_v)
            if norm_v <= cutoff_distance:
                met_theta = vector_angle(vector_v, dict_met['vector_a'])
                met_phi = vector_angle(vector_v, dict_met['vector_g'])
                if (met_theta <= cutoff_angle) or (met_phi <= cutoff_angle):
                    results.append({
                        'aromatic_residue': midpoint[1],
                        'aromatic_position': int(midpoint[0]),
                        'methionine_position': int(dict_met['position']),
                        'norm': round(norm_v, ROUND_TO_NUMBER),
                        'met_theta_angle': round(met_theta, ROUND_TO_NUMBER),
                        'met_phi_angle': round(met_phi, ROUND_TO_NUMBER)
                    })
                else:
                    pass
            else:
                pass
    return results
