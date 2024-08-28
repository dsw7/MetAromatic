from dataclasses import dataclass, field
from pathlib import Path
from typing import TypedDict
from pydantic import BaseModel
from .aliases import Midpoints, Coordinates, Models, FloatArray


class DictInteractions(TypedDict):
    aromatic_position: int
    aromatic_residue: str
    met_phi_angle: float
    met_theta_angle: float
    methionine_position: int
    norm: float


class MetAromaticParams(BaseModel):
    chain: str
    cutoff_angle: float
    cutoff_distance: float
    model: Models


class BatchParams(BaseModel):
    collection: str
    database: str
    host: str
    overwrite: bool
    password: str
    path_batch_file: Path
    port: int
    threads: int
    username: str


@dataclass
class LonePairs:
    coords_sd: FloatArray
    position: str
    vector_a: FloatArray
    vector_g: FloatArray


@dataclass
class Interactions:
    aromatic_position: int
    aromatic_residue: str
    met_phi_angle: float
    met_theta_angle: float
    methionine_position: int
    norm: float

    def to_dict(self) -> DictInteractions:
        # __dict__ will throw mypy error since the type is dict[str, Any]
        return DictInteractions(
            aromatic_position=self.aromatic_position,
            aromatic_residue=self.aromatic_residue,
            met_phi_angle=self.met_phi_angle,
            met_theta_angle=self.met_theta_angle,
            methionine_position=self.methionine_position,
            norm=self.norm,
        )


@dataclass
class FeatureSpace:
    first_model: list[str] = field(default_factory=list)
    coords_met: Coordinates = field(default_factory=list)
    coords_phe: Coordinates = field(default_factory=list)
    coords_tyr: Coordinates = field(default_factory=list)
    coords_trp: Coordinates = field(default_factory=list)
    lone_pairs_met: list[LonePairs] = field(default_factory=list)
    midpoints_phe: Midpoints = field(default_factory=list)
    midpoints_tyr: Midpoints = field(default_factory=list)
    midpoints_trp: Midpoints = field(default_factory=list)
    interactions: list[Interactions] = field(default_factory=list)

    def serialize_interactions(self) -> list[DictInteractions]:
        return [i.to_dict() for i in self.interactions]


@dataclass
class BridgeSpace:
    interactions: set[tuple[str, str]] = field(default_factory=set)
    bridges: list[set[str]] = field(default_factory=list)
