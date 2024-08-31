from enum import Enum
from numpy import sin, cos, pi


# CLI
class Help(Enum):

    CMD_BATCH = "Run a Met-aromatic query batch job."
    CMD_BRIDGE = "Run a bridging interaction query on a single PDB entry."
    CMD_PAIR = "Run a Met-aromatic query against a single PDB entry."
    CMD_READ_LOCAL = "Run a Met-aromatic query against a local PDB file."

    ANGLE = "Specify a cutoff angle in degrees."
    CHAIN = "Specify a chain ID."
    DIST = "Specify a cutoff distance in Angstroms."
    MODEL = "Specify a lone pair interpolation model."

    COLL = "Specify MongoDB collection to use."
    DB = "Specify MongoDB database to use."
    HOST = "Specify host name."
    OVERWRITE = "Specify whether to overwrite collection."
    PASSWORD = "Specify MongoDB password if authentication is enabled."
    PORT = "Specify MongoDB TCP connection port."
    THREADS = "Specify number of workers to use."
    USERNAME = "Specify MongoDB username if authentication is enabled."
    VERTICES = "Specify number of vertices."


# Linear algebra
# See https://en.wikipedia.org/wiki/Rodrigues%27_rotation_formula "Matrix notation" section
SCAL1 = sin(pi / 2)
SCAL2 = 1 - cos(pi / 2)
ROOT_2 = 2**0.5

# Keys for computing aromatic midpoints
DICT_ATOMS_PHE = {"CG": "A", "CD2": "B", "CE2": "C", "CZ": "D", "CE1": "E", "CD1": "F"}
DICT_ATOMS_TYR = {"CG": "A", "CD2": "B", "CE2": "C", "CZ": "D", "CE1": "E", "CD1": "F"}
DICT_ATOMS_TRP = {
    "CD2": "A",
    "CE3": "B",
    "CZ3": "C",
    "CH2": "D",
    "CZ2": "E",
    "CE2": "F",
}
