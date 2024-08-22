from dataclasses import dataclass, field
from typing import Literal
from numpy import ndarray
from pydantic import BaseModel
from .aliases import Midpoints, Coordinates


class MetAromaticParams(BaseModel):
    chain: str
    cutoff_angle: float
    cutoff_distance: float
    model: Literal["cp", "rm"]


class BatchParams(BaseModel):
    collection: str
    database: str
    host: str
    overwrite: bool
    password: str
    path_batch_file: str
    port: int
    threads: int
    username: str


@dataclass
class LonePairs:
    coords_sd: ndarray
    position: str
    vector_a: ndarray
    vector_g: ndarray


@dataclass
class Interactions:
    aromatic_position: int
    aromatic_residue: str
    met_phi_angle: float
    met_theta_angle: float
    methionine_position: int
    norm: float

    def print_interaction(self) -> None:
        print(
            f"{self.aromatic_residue:<10} "
            f"{self.aromatic_position:<10} "
            f"{self.methionine_position:<10} "
            f"{self.norm:<10} "
            f"{self.met_theta_angle:<10} "
            f"{self.met_phi_angle:<10}"
        )


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
    interactions: list[Interactions] = field(default_factory=list)
    OK: bool = True
    status: str = "Success"

    def print_interactions(self) -> None:
        print("ARO        POS        MET POS    NORM       MET-THETA  MET-PHI")

        for i in self.interactions:
            i.print_interaction()


@dataclass
class BridgeSpace:
    interactions: set[tuple[str, str]] = field(default_factory=set)
    bridges: list[set[str]] = field(default_factory=list)
    OK: bool = True
    status: str = "Success"

    def print_bridges(self) -> None:
        for bridge in self.bridges:
            print("{" + "}-{".join(bridge) + "}")
