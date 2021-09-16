from numpy.linalg import norm
from .cross_product_method import vector_angle

ROUND_TO_NUMBER = 3

def apply_distance_angular_condition(midpoints: list, lone_pairs: list, cutoff_distance: float, cutoff_angle: float) -> list:
    met_aromatic_interactions = []

    for lone_pair_data in lone_pairs:
        for midpoint in midpoints:

            v = midpoint[2] - lone_pair_data['coords_sd']
            norm_v = norm(v)

            if norm_v <= cutoff_distance:

                met_theta_angle = vector_angle(v, lone_pair_data['vector_a'])
                met_phi_angle = vector_angle(v, lone_pair_data['vector_g'])

                if (met_theta_angle <= cutoff_angle) or (met_phi_angle <= cutoff_angle):
                    result = {
                        'aromatic_residue': midpoint[1],
                        'aromatic_position': int(midpoint[0]),
                        'methionine_position': int(lone_pair_data['position']),
                        'norm': round(norm_v, ROUND_TO_NUMBER),
                        'met_theta_angle': round(met_theta_angle, ROUND_TO_NUMBER),
                        'met_phi_angle': round(met_phi_angle, ROUND_TO_NUMBER)
                    }
                    met_aromatic_interactions.append(result)

                else:
                    pass
            else:
                pass

    return met_aromatic_interactions
