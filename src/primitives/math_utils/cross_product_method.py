from numpy import degrees
from numpy import linalg
from numpy import cross
from numpy import arccos
from numpy import dot


def vector_angle(vec_u, vec_v):
    num = dot(vec_u, vec_v)
    den = linalg.norm(vec_v) * linalg.norm(vec_u)
    return degrees(arccos(num / den))

def unit_vec(vec):
    return vec / linalg.norm(vec)

class CrossProductMethod:
    """
    A class for computing the vectors parallel to MET SD lone pairs
    Methods associated with the class complete the vertices of a tetrahedron
    """
    def __init__(self, terminal_a, midpoint, terminal_b):
        self.terminal_a = terminal_a
        self.midpoint = midpoint
        self.terminal_b = terminal_b
        self.vec_u = self.terminal_a - self.midpoint
        self.vec_v = self.terminal_b - self.midpoint
        self.anti_parallel_vec = unit_vec(-0.5 * (unit_vec(self.vec_v) + unit_vec(self.vec_u)))

    def get_vector_a(self):
        cross_vec = cross(self.vec_u, self.vec_v)
        return self.anti_parallel_vec + 2**0.5 * unit_vec(cross_vec)

    def get_vector_g(self):
        cross_vec = cross(self.vec_v, self.vec_u)
        return self.anti_parallel_vec + 2**0.5 * unit_vec(cross_vec)
