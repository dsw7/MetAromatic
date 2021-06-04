# pylint: disable=C0103 # Disable "Argument name "u" doesn't conform to snake_case naming style"

from numpy import (
    degrees,
    linalg,
    cross,
    arccos,
    dot,
    ndarray
)

def vector_angle(u: ndarray, v: ndarray) -> float:
    numerator = dot(u, v)
    denominator = linalg.norm(v) * linalg.norm(u)
    return degrees(arccos(numerator / denominator))

def get_unit_vector(v: ndarray) -> ndarray:
    return v / linalg.norm(v)

class CrossProductMethod:
    """
    A class for computing the vectors parallel to MET SD lone pairs
    Methods associated with the class complete the vertices of a tetrahedron
    """

    def __init__(self, terminal_a: ndarray, midpoint: ndarray, terminal_b: ndarray) -> None:

        self.terminal_a = terminal_a
        self.midpoint = midpoint
        self.terminal_b = terminal_b

        self.u = self.terminal_a - self.midpoint
        self.v = self.terminal_b - self.midpoint

        self.anti_parallel_vec = get_unit_vector(
            -0.5 * (get_unit_vector(self.v) + get_unit_vector(self.u))
        )

    def get_vector_a(self) -> ndarray:
        cross_vec = cross(self.u, self.v)
        return self.anti_parallel_vec + 2**0.5 * get_unit_vector(cross_vec)

    def get_vector_g(self) -> ndarray:
        cross_vec = cross(self.v, self.u)
        return self.anti_parallel_vec + 2**0.5 * get_unit_vector(cross_vec)
