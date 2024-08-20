from functools import cache
from os import get_terminal_size
from numpy import ndarray, linalg, eye, dot, degrees, arccos


@cache
def get_separator() -> str:
    try:
        separator = get_terminal_size()[0] * "-"
    except OSError:
        separator = 25 * "-"

    return separator


def print_separator() -> None:
    print(get_separator())


def get_unit_vector(v: ndarray) -> ndarray:
    return v / linalg.norm(v)


@cache
def get_3x3_identity_matrix() -> ndarray:
    return eye(3)


def get_angle_between_vecs(u: ndarray, v: ndarray) -> float:
    dot_product = dot(u, v)
    cross_product = linalg.norm(v) * linalg.norm(u)

    return degrees(arccos(dot_product / cross_product))
