from typing import Union
from itertools import groupby
from copy import deepcopy
from operator import itemgetter
from numpy import array, ndarray

DICT_ATOMS_PHE = {
    'CG': 'A', 'CD2': 'B', 'CE2': 'C',
    'CZ': 'D', 'CE1': 'E', 'CD1': 'F'
}

DICT_ATOMS_TYR = {
    'CG': 'A', 'CD2': 'B', 'CE2': 'C',
    'CZ': 'D', 'CE1': 'E', 'CD1': 'F'
}

DICT_ATOMS_TRP = {
    'CD2': 'A', 'CE3': 'B', 'CZ3': 'C',
    'CH2': 'D', 'CZ2': 'E', 'CE2': 'F'
}

def get_hexagon_midpoints(x: list[int], y: list[int], z: list[int]) -> tuple[list[int]]:

    """
    Function for computing midpoints between vertices in a hexagon
    Parameters:
        x, y, z -> list objects of x, y, and z hexagon coordinates
    Returns:
        x_mid, y_mid, z_mid -> a list of x, y, and z hexagon midpoint coordinates
    """

    x_f = x[1:] + [x[0]]
    y_f = y[1:] + [y[0]]
    z_f = z[1:] + [z[0]]

    x_mid = [0.5 * (a + b) for a, b in zip(x, x_f)]
    y_mid = [0.5 * (a + b) for a, b in zip(y, y_f)]
    z_mid = [0.5 * (a + b) for a, b in zip(z, z_f)]

    return x_mid, y_mid, z_mid

def get_aromatic_midpoints(aromatics: list[list[str]], keys: dict[str, str]) -> list[list[Union[str, ndarray]]]:

    aromatics = [
        list(group) for _, group in groupby(aromatics, lambda entry: entry[5])
    ]

    midpoints = []

    for grouped in deepcopy(aromatics):

        # Map unique values to atomic label keys
        for row in grouped:
            row[2] = keys.get(row[2])

        # Sort based on these values which are just A, B, C, D, E, F
        ordered = sorted(grouped, key=itemgetter(2))

        x_coord = [float(i[6]) for i in ordered]
        y_coord = [float(i[7]) for i in ordered]
        z_coord = [float(i[8]) for i in ordered]

        x_mid, y_mid, z_mid = get_hexagon_midpoints(x_coord, y_coord, z_coord)

        for a, b, c in zip(x_mid, y_mid, z_mid):
            midpoints.append([ordered[0][5], ordered[0][3], array([a, b, c])])

    return midpoints

def get_phe_midpoints(phe_coords: list[list[str]]) -> list[list[Union[str, ndarray]]]:
    return get_aromatic_midpoints(phe_coords, DICT_ATOMS_PHE)

def get_tyr_midpoints(tyr_coords: list[list[str]]) -> list[list[Union[str, ndarray]]]:
    return get_aromatic_midpoints(tyr_coords, DICT_ATOMS_TYR)

def get_trp_midpoints(trp_coords: list[list[str]]) -> list[list[Union[str, ndarray]]]:
    return get_aromatic_midpoints(trp_coords, DICT_ATOMS_TRP)
