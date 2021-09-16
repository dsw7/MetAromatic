from itertools import groupby
from copy import deepcopy
from operator import itemgetter
from numpy import array
from .get_hexagon_midpoints import get_hexagon_midpoints

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

def get_aromatic_midpoints(aromatics: list, keys: dict) -> list:
    aromatics = [
        list(group) for _, group in groupby(aromatics, lambda entry: entry[5])
    ]

    midpoints = []

    # Fix for self.phenylalanines A, B, C bug
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

def get_phe_midpoints(phenylalanine_coords: list) -> list:
    return get_aromatic_midpoints(phenylalanine_coords, DICT_ATOMS_PHE)

def get_tyr_midpoints(tyrosine_coords: list) -> list:
    return get_aromatic_midpoints(tyrosine_coords, DICT_ATOMS_TYR)

def get_trp_midpoints(tryptophan_coords: list) -> list:
    return get_aromatic_midpoints(tryptophan_coords, DICT_ATOMS_TRP)
