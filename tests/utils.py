from typing import TypedDict
from unittest import TestCase
from MetAromatic.aliases import Models
from MetAromatic.models import DictInteractions


class Defaults(TypedDict):
    chain: str
    cutoff_angle: float
    cutoff_distance: float
    model: Models


def compare_interactions(
    left: list[DictInteractions], right: list[DictInteractions]
) -> None:
    tc = TestCase()
    tc.maxDiff = None
    tc.assertCountEqual(left, right)
