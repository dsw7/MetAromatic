from typing import TypeAlias, Literal
from numpy import ndarray

Coordinates: TypeAlias = list[list[str]]
Midpoints: TypeAlias = list[tuple[str, str, ndarray]]
RawData: TypeAlias = list[str]
Residues: TypeAlias = Literal["phe", "tyr", "trp", "met"]
