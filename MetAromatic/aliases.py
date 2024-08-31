from typing import TypeAlias, Literal
from numpy import float64
from numpy.typing import NDArray

FloatArray: TypeAlias = NDArray[float64]

Coordinates: TypeAlias = list[list[str]]
Midpoints: TypeAlias = list[tuple[str, str, FloatArray]]
Models: TypeAlias = Literal["cp", "rm"]
RawData: TypeAlias = list[str]
Residues: TypeAlias = Literal["phe", "tyr", "trp", "met"]

PdbCodes: TypeAlias = list[str]
Chunks: TypeAlias = list[PdbCodes]
