# pylint: disable=C0103 # Disable "Argument name "u" doesn't conform to snake_case naming style"

from numpy import (
    sin,
    cos,
    pi,
    linalg,
    matmul,
    array,
    eye,
    ndarray
)

SCAL1 = sin(pi / 2)
SCAL2 = 1 - cos(pi / 2)

class RodriguesMethod:

    """
    Here I use Rodrigues' rotation formula for completing the vertices
    of a regular tetrahedron. To start, we know two vertices of a tetrahedron,
    A and B, in addition to knowing the origin O. So we map A and B to the
    origin of the frame in which the tetrahedron resides by computing
    u = A - O and v = B - O. The directions of u, v are then flipped by scaling
    u, v by -1. We then take -u, -v and rotate the vectors by 90 degrees about
    k, where k is the line of intersection between the two orthogonal planes
    of the tetrahedron. These rotated vectors now describe the position of the
    remaining coordinates C, D. We have our tetrahedron with vertices A, B,
    C, D and the origin O.
    """

    def __init__(self, vertex_a: ndarray, origin: ndarray, vertex_b: ndarray) -> None:
        # map to origin
        u = vertex_a - origin
        v = vertex_b - origin

        # flip direction
        self.u = -1 * u
        self.v = -1 * v

        # we then find the vector about which we rotate
        r = 0.5 * (self.u + self.v)

        # then find unit vector of r
        r_hat = r / linalg.norm(r)

        # get components of the unit vector r
        r_hat_x = r_hat[0]
        r_hat_y = r_hat[1]
        r_hat_z = r_hat[2]

        # get the W array
        W = array(
            [[0, -r_hat_z, r_hat_y],
             [r_hat_z, 0, -r_hat_x],
             [-r_hat_y, r_hat_x, 0]]
        )

        # then construct Rodrigues rotation array
        self.rodrigues_rotation_matrix = array(eye(3)) + (SCAL1 * W) + (SCAL2 * matmul(W, W))

    # note that I flipped these methods to match previous algorithm
    def get_vector_g(self) -> list:
        return matmul(self.rodrigues_rotation_matrix, self.u).tolist()

    def get_vector_a(self) -> list:
        return matmul(self.rodrigues_rotation_matrix, self.v).tolist()
