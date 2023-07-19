from itertools import groupby
from copy import deepcopy
from operator import itemgetter
from numpy import array
from MetAromatic.complex_types import TYPE_MIDPOINTS

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

def get_midpoints(c: list[float]) -> list[float]:

    c_f = c[1:] + [c[0]]

    return [0.5 * (a + b) for a, b in zip(c, c_f)]

def get_aromatic_midpoints(aromatics: list[list[str]], keys: dict[str, str]) -> list[TYPE_MIDPOINTS]:

    aromatics_grouped = [
        list(group) for _, group in groupby(aromatics, lambda e: e[5])
    ]

    midpoints = []

    for group in deepcopy(aromatics_grouped):

        # Map unique values to atomic label keys
        for row in group:
            row[2] = keys[row[2]]

        # Sort based on these values which are just A, B, C, D, E, F
        ordered = sorted(group, key=itemgetter(2))

        x_coord = [float(i[6]) for i in ordered]
        y_coord = [float(i[7]) for i in ordered]
        z_coord = [float(i[8]) for i in ordered]

        x_mid = get_midpoints(x_coord)
        y_mid = get_midpoints(y_coord)
        z_mid = get_midpoints(z_coord)

        for a, b, c in zip(x_mid, y_mid, z_mid):
            midpoints.append(
                (ordered[0][5], ordered[0][3], array([a, b, c]))
            )

    return midpoints

def get_phe_midpoints(phe_coords: list[list[str]]) -> list[TYPE_MIDPOINTS]:
    return get_aromatic_midpoints(phe_coords, DICT_ATOMS_PHE)

def get_tyr_midpoints(tyr_coords: list[list[str]]) -> list[TYPE_MIDPOINTS]:
    return get_aromatic_midpoints(tyr_coords, DICT_ATOMS_TYR)

def get_trp_midpoints(trp_coords: list[list[str]]) -> list[TYPE_MIDPOINTS]:
    return get_aromatic_midpoints(trp_coords, DICT_ATOMS_TRP)
