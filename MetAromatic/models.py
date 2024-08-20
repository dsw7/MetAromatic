from dataclasses import dataclass, field
from typing import Literal, TypedDict
from numpy import ndarray
from pydantic import BaseModel
from .complex_types import Midpoints


class MetAromaticParams(BaseModel):
    chain: str
    cutoff_angle: float
    cutoff_distance: float
    model: Literal["cp", "rm"]


TYPE_LONE_PAIRS_MET = TypedDict(
    "TYPE_LONE_PAIRS_MET",
    {"coords_sd": ndarray, "position": str, "vector_a": ndarray, "vector_g": ndarray},
)

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
class FeatureSpace:
    raw_data: list[str] = field(default_factory=list)
    first_model: list[str] = field(default_factory=list)
    coords_met: list[list[str]] = field(default_factory=list)
    coords_phe: list[list[str]] = field(default_factory=list)
    coords_tyr: list[list[str]] = field(default_factory=list)
    coords_trp: list[list[str]] = field(default_factory=list)
    lone_pairs_met: list[TYPE_LONE_PAIRS_MET] = field(default_factory=list)
    midpoints_phe: list[Midpoints] = field(default_factory=list)
    midpoints_tyr: list[Midpoints] = field(default_factory=list)
    midpoints_trp: list[Midpoints] = field(default_factory=list)
    interactions: list[TYPE_INTERACTIONS] = field(default_factory=list)
    OK: bool = True
    status: str = "Success"
