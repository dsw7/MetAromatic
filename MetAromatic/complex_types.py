from typing import TypeAlias, Literal
from numpy import ndarray

Coordinates: TypeAlias = list[list[str]]
Midpoints: TypeAlias = list[tuple[str, str, ndarray]]
Residues: TypeAlias = Literal["phe", "tyr", "trp", "met"]
