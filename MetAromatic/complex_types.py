from typing import TypedDict, TypeAlias
from numpy import ndarray

Coordinates: TypeAlias = list[list[str]]
Midpoints: TypeAlias = list[tuple[str, str, ndarray]]

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


TYPE_BRIDGE_SPACE = TypedDict(
    "TYPE_BRIDGE_SPACE",
    {
        "interactions": set[tuple[str, str]],
        "bridges": list[set[str]],
        "OK": bool,
        "status": str,
    },
)
