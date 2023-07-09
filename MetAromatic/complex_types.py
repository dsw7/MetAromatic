from typing import TypedDict
from numpy import ndarray

TYPE_MIDPOINTS = tuple[str, str, ndarray]

TYPE_LONE_PAIRS_MET = TypedDict(
    'TYPE_LONE_PAIRS_MET',
    {
        'coords_sd': ndarray,
        'position': str,
        'vector_a': ndarray,
        'vector_g': ndarray
    }
)

TYPE_INTERACTIONS = TypedDict(
    'TYPE_INTERACTIONS',
    {
        'aromatic_position': int,
        'aromatic_residue': str,
        'met_phi_angle': float,
        'met_theta_angle': float,
        'methionine_position': int,
        'norm': float
    }
)
