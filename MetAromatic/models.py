from typing import Literal
from pydantic import BaseModel


class MetAromaticParams(BaseModel):
    chain: str
    cutoff_angle: float
    cutoff_distance: float
    model: Literal["cp", "rm"]
