# Written by David Weber
# dsw7@sfu.ca

""" All functions required for running low level Met-Aromatic implementation """

# ----------------------------------------------------------------------------

from numpy import sin, cos, pi
from numpy import degrees
from numpy import linalg
from numpy import cross
from numpy import matmul
from numpy import matrix
from numpy import arccos
from numpy import eye
from numpy import dot

SCAL1 = sin(pi / 2)
SCAL2 = 1 - cos(pi / 2)

def vector_angle(u, v):
    # a routine for computing angle between two vectors
    num = dot(u, v)
    den = linalg.norm(v) * linalg.norm(u)
    return degrees(arccos(num / den))

def unit_vec(v):
    # get the unit vector of a vector
    return v / linalg.norm(v)
    
def get_hexagon_midpoints(x, y, z):
    """
    Function for computing midpoints between vertices in a hexagon
    Parameters:
        x, y, z -> list objects of x, y, and z hexagon coordinates
    Returns:
        x_mid, y_mid, z_mid -> a list of x, y, and z hexagon midpoint coordinates
    """
    
    # offset each list by 1
    x_f = x[1:] + [x[0]]
    y_f = y[1:] + [y[0]]
    z_f = z[1:] + [z[0]]

    # compute means between original and offset lists
    x_mid = [0.5 * (a + b) for a, b in zip(x, x_f)]
    y_mid = [0.5 * (a + b) for a, b in zip(y, y_f)]
    z_mid = [0.5 * (a + b) for a, b in zip(z, z_f)]
    
    return x_mid, y_mid, z_mid

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
        
        # get the W matrix
        W = matrix([[0, -r_hat_z, r_hat_y],
                    [r_hat_z, 0, -r_hat_x],
                    [-r_hat_y, r_hat_x, 0]])
                       
        # then construct Rodrigues rotation matrix
        self.R = matrix(eye(3)) + (SCAL1 * W) + (SCAL2 * matmul(W, W))
    
    # note that I flipped these methods to match previous algorithm
    def vector_g(self):
        # get vector g - first vertex
        return matmul(self.R, self.vec_u).tolist()[0]

    def vector_a(self):
        # get vector v - second vertex
        return matmul(self.R, self.vec_v).tolist()[0]

class LonePairs:
    # a class for computing the vectors parallel to MET SD lone pairs
    # methods associated with the class complete the vertices of a tetrahedron
    # made this one in my undergrad
    def __init__(self, terminal_a, midpoint, terminal_b):
        self.terminal_a = terminal_a
        self.midpoint = midpoint
        self.terminal_b = terminal_b
        self.u = self.terminal_a - self.midpoint  # mapping to origin
        self.v = self.terminal_b - self.midpoint  # mapping to origin
        self.NOT_vec = unit_vec(-0.5 * (unit_vec(self.v) + unit_vec(self.u)))
        
    def vector_a(self):
        cross_vec = cross(self.u, self.v)
        return self.NOT_vec + 2**0.5 * unit_vec(cross_vec)
        
    def vector_g(self):
        cross_vec = cross(self.v, self.u)
        return self.NOT_vec + 2**0.5 * unit_vec(cross_vec)