from typing import TypedDict, TypeAlias, Literal
from numpy import ndarray

Coordinates: TypeAlias = list[list[str]]
Midpoints: TypeAlias = list[tuple[str, str, ndarray]]
Residues: TypeAlias = Literal["phe", "tyr", "trp", "met"]

TYPE_BATCH_PARAMS = TypedDict(
    "TYPE_BATCH_PARAMS",
    {
        "path_batch_file": str,
        "threads": int,
        "host": str,
        "port": int,
        "database": str,
        "collection": str,
        "overwrite": bool,
        "uri": str,
    },
)
