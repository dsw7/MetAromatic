from typing import TypedDict
from numpy import ndarray

TYPE_MA_PARAMS = TypedDict(
    'TYPE_MA_PARAMS',
    {
        'cutoff_distance': float,
        'cutoff_angle': float,
        'chain': str,
        'model': str
    }
)

TYPE_BATCH_PARAMS = TypedDict(
    'TYPE_BATCH_PARAMS',
    {
        'path_batch_file': str,
        'threads': int,
        'host': str,
        'port': int,
        'database': str,
        'collection': str,
        'overwrite': bool,
        'uri': str
    }
)

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

TYPE_FEATURE_SPACE = TypedDict(
    'TYPE_FEATURE_SPACE',
    {
        'cutoff_dist': float,
        'cutoff_angle': float,
        'chain': str,
        'model': str,
        'raw_data': list[str],
        'first_model': list[str],
        'coords_met': list[list[str]],
        'coords_phe': list[list[str]],
        'coords_tyr': list[list[str]],
        'coords_trp': list[list[str]],
        'lone_pairs_met': list[TYPE_LONE_PAIRS_MET],
        'midpoints_phe': list[TYPE_MIDPOINTS],
        'midpoints_tyr': list[TYPE_MIDPOINTS],
        'midpoints_trp': list[TYPE_MIDPOINTS],
        'interactions': list[TYPE_INTERACTIONS],
        'OK': bool,
        'status': str,
    }
)

TYPE_BRIDGE_SPACE = TypedDict(
    'TYPE_BRIDGE_SPACE',
    {
        'interactions': set[tuple[str, str]],
        'bridges': list[set[str]],
        'OK': bool,
        'status': str,
    }
)
