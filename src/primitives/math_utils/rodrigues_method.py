from numpy import sin, cos, pi
from numpy import linalg
from numpy import matmul
from numpy import array
from numpy import eye


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
    def __init__(self, vertex_a, origin, vertex_b):
        # map to origin
        vec_u = vertex_a - origin
        vec_v = vertex_b - origin

        # flip direction
        self.vec_u = -1 * vec_u
        self.vec_v = -1 * vec_v

        # we then find the vector about which we rotate
        r = 0.5 * (self.vec_u + self.vec_v)

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
        self.rodrigues = array(eye(3)) + (SCAL1 * W) + (SCAL2 * matmul(W, W))

    # note that I flipped these methods to match previous algorithm
    def get_vector_g(self):
        return matmul(self.rodrigues, self.vec_u).tolist()

    def get_vector_a(self):
        return matmul(self.rodrigues, self.vec_v).tolist()
