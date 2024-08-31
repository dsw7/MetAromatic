from functools import cache
from os import get_terminal_size
from re import compile, Pattern  # pylint: disable=redefined-builtin
from typing import Any
from numpy import linalg, eye, dot, degrees, arccos
from .aliases import Residues, FloatArray


@cache
def _get_separator() -> str:
    try:
        separator = get_terminal_size()[0] * "-"
    except OSError:
        separator = 25 * "-"

    return separator


def print_separator() -> None:
    print(_get_separator())


def get_unit_vector(v: FloatArray) -> FloatArray:
    return v / linalg.norm(v)


@cache
def get_3x3_identity_matrix() -> Any:
    # No good way to type hint this yet
    # See https://github.com/numpy/numpy/issues/16544#issuecomment-1058675773
    return eye(3)


def get_angle_between_vecs(u: FloatArray, v: FloatArray) -> float:
    dot_product = dot(u, v)
    cross_product = linalg.norm(v) * linalg.norm(u)

    angle: float = degrees(arccos(dot_product / cross_product)).item()
    return angle


def _get_met_search_pattern(chain: str) -> Pattern[str]:
    return compile(rf"(ATOM.*(CE|SD|CG)\s+MET\s+{chain}\s)")


def _get_phe_search_pattern(chain: str) -> Pattern[str]:
    return compile(rf"(ATOM.*(CD1|CE1|CZ|CG|CD2|CE2)\s+PHE\s+{chain}\s)")


def _get_tyr_search_pattern(chain: str) -> Pattern[str]:
    return compile(rf"(ATOM.*(CD1|CE1|CZ|CG|CD2|CE2)\s+TYR\s+{chain}\s)")


def _get_trp_search_pattern(chain: str) -> Pattern[str]:
    return compile(rf"(ATOM.*(CD2|CE3|CZ2|CH2|CZ3|CE2)\s+TRP\s+{chain}\s)")


@cache
def get_search_pattern(res: Residues, chain: str) -> Pattern[str]:
    pattern: Pattern[str]

    if res == "met":
        pattern = _get_met_search_pattern(chain)
    elif res == "phe":
        pattern = _get_phe_search_pattern(chain)
    elif res == "tyr":
        pattern = _get_tyr_search_pattern(chain)
    else:
        pattern = _get_trp_search_pattern(chain)

    return pattern
