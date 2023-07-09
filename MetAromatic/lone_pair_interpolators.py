# pylint: disable=C0103 # Disable "Argument name "u" doesn't conform to snake_case naming style"

import numpy as np

SCAL1 = np.sin(np.pi / 2)
SCAL2 = 1 - np.cos(np.pi / 2)
ROOT_2 = 2 ** 0.5

def get_unit_vector(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v)


class CrossProductMethod:

    """
    A class for computing the vectors parallel to MET SD lone pairs Methods associated with the class complete
    the vertices of a tetrahedron
    """

    def __init__(self, terminal_a: np.ndarray, midpoint: np.ndarray, terminal_b: np.ndarray) -> None:

        self.terminal_a = terminal_a
        self.midpoint = midpoint
        self.terminal_b = terminal_b

        self.u = self.terminal_a - self.midpoint
        self.v = self.terminal_b - self.midpoint

        self.anti_parallel_vec = get_unit_vector(-0.5 * (get_unit_vector(self.v) + get_unit_vector(self.u)))

    def get_vector_a(self) -> np.ndarray:

        cross_vec = np.cross(self.u, self.v)
        return self.anti_parallel_vec + ROOT_2 * get_unit_vector(cross_vec)

    def get_vector_g(self) -> np.ndarray:

        cross_vec = np.cross(self.v, self.u)
        return self.anti_parallel_vec + ROOT_2 * get_unit_vector(cross_vec)


class RodriguesMethod:

    """
    Here I use Rodrigues' rotation formula for completing the vertices of a regular tetrahedron. To start, we
    know two vertices of a tetrahedron, A and B, in addition to knowing the origin O. So we map A and B to the
    origin of the frame in which the tetrahedron resides by computing u = A - O and v = B - O. The directions
    of u, v are then flipped by scaling u, v by -1. We then take -u, -v and rotate the vectors by 90 degrees
    about k, where k is the line of intersection between the two orthogonal planes of the tetrahedron. These
    rotated vectors now describe the position of the remaining coordinates C, D. We have our tetrahedron with
    vertices A, B, C, D and the origin O.
    """

    def __init__(self, vertex_a: np.ndarray, origin: np.ndarray, vertex_b: np.ndarray) -> None:

        # Map to origin
        u = vertex_a - origin
        v = vertex_b - origin

        # Flip direction
        self.u = -1 * u
        self.v = -1 * v

        # We then find the vector about which we rotate
        r = 0.5 * (self.u + self.v)

        # Then find unit vector of r
        r_hat = r / np.linalg.norm(r)

        # Get components of the unit vector r
        r_hat_x = r_hat[0]
        r_hat_y = r_hat[1]
        r_hat_z = r_hat[2]

        # Get the W array
        W = np.array(
            [[0, -r_hat_z, r_hat_y],
             [r_hat_z, 0, -r_hat_x],
             [-r_hat_y, r_hat_x, 0]]
        )

        # Then construct Rodrigues rotation array
        self.rodrigues_rotation_matrix = np.array(np.eye(3)) + (SCAL1 * W) + (SCAL2 * np.matmul(W, W))

    # Note that I flipped these methods to match previous algorithm
    def get_vector_g(self) -> np.ndarray:
        return np.matmul(self.rodrigues_rotation_matrix, self.u)

    def get_vector_a(self) -> np.ndarray:
        return np.matmul(self.rodrigues_rotation_matrix, self.v)
