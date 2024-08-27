from unittest import TestCase
from MetAromatic.models import DictInteractions


def compare_interactions(
    left: list[DictInteractions], right: list[DictInteractions]
) -> None:
    tc = TestCase()
    tc.maxDiff = None
    tc.assertCountEqual(left, right)
