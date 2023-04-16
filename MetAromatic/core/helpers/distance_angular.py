import numpy as np

def vector_angle(u: np.ndarray, v: np.ndarray) -> float:

    numerator = np.dot(u, v)
    denominator = np.linalg.norm(v) * np.linalg.norm(u)

    return np.degrees(np.arccos(numerator / denominator))

def apply_distance_angular_condition(midpoints: list, lone_pairs: list, cutoff_distance: float, cutoff_angle: float) -> list:
    met_aromatic_interactions = []

    for lone_pair_data in lone_pairs:
        for midpoint in midpoints:

            v = midpoint[2] - lone_pair_data['coords_sd']
            norm_v = np.linalg.norm(v)

            if norm_v <= cutoff_distance:

                met_theta_angle = vector_angle(v, lone_pair_data['vector_a'])
                met_phi_angle = vector_angle(v, lone_pair_data['vector_g'])

                if (met_theta_angle <= cutoff_angle) or (met_phi_angle <= cutoff_angle):
                    result = {
                        'aromatic_residue': midpoint[1],
                        'aromatic_position': int(midpoint[0]),
                        'methionine_position': int(lone_pair_data['position']),
                        'norm': round(norm_v, 3),
                        'met_theta_angle': round(met_theta_angle, 3),
                        'met_phi_angle': round(met_phi_angle, 3)
                    }
                    met_aromatic_interactions.append(result)

                else:
                    pass
            else:
                pass

    return met_aromatic_interactions
