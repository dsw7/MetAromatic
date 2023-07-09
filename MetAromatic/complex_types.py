from typing import TypedDict
from numpy import ndarray

TYPE_LONE_PAIRS_MET = TypedDict(
    'TYPE_LONE_PAIRS_MET',
    {
        'vector_a': ndarray,
        'vector_g': ndarray,
        'coords_sd': ndarray,
        'position': str
    }
)
