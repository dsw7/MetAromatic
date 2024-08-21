from dataclasses import dataclass, field
from typing import Literal, TypedDict
from numpy import ndarray
from pydantic import BaseModel
from .complex_types import Midpoints, Coordinates


class MetAromaticParams(BaseModel):
    chain: str
    cutoff_angle: float
    cutoff_distance: float
    model: Literal["cp", "rm"]


TYPE_INTERACTIONS = TypedDict(
    "TYPE_INTERACTIONS",
    {
        "aromatic_position": int,
        "aromatic_residue": str,
        "met_phi_angle": float,
        "met_theta_angle": float,
        "methionine_position": int,
        "norm": float,
    },
)


@dataclass
class LonePairs:
    coords_sd: ndarray
    position: str
    vector_a: ndarray
    vector_g: ndarray


@dataclass
class FeatureSpace:
    raw_data: list[str] = field(default_factory=list)
    first_model: list[str] = field(default_factory=list)
    coords_met: Coordinates = field(default_factory=list)
    coords_phe: Coordinates = field(default_factory=list)
    coords_tyr: Coordinates = field(default_factory=list)
    coords_trp: Coordinates = field(default_factory=list)
    lone_pairs_met: list[LonePairs] = field(default_factory=list)
    midpoints_phe: Midpoints = field(default_factory=list)
    midpoints_tyr: Midpoints = field(default_factory=list)
    midpoints_trp: Midpoints = field(default_factory=list)
    interactions: list[TYPE_INTERACTIONS] = field(default_factory=list)
    OK: bool = True
    status: str = "Success"
