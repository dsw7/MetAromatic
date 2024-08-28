from itertools import groupby
from copy import deepcopy
from operator import itemgetter
from numpy import array
from .aliases import Midpoints, Coordinates, FloatArray
from .consts import DICT_ATOMS_PHE, DICT_ATOMS_TYR, DICT_ATOMS_TRP


def get_midpoints(c: list[float]) -> list[float]:
    c_f = c[1:] + [c[0]]

    return [0.5 * (a + b) for a, b in zip(c, c_f)]


def _get_aromatic_midpoints(aromatics: Coordinates, keys: dict[str, str]) -> Midpoints:
    aromatics_grouped = [list(group) for _, group in groupby(aromatics, lambda e: e[5])]

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

        for x, y, z in zip(x_mid, y_mid, z_mid):
            residue_pos: str = ordered[0][5]
            residue_name: str = ordered[0][3]
            coords: FloatArray = array([x, y, z])

            midpoints.append((residue_pos, residue_name, coords))

    return midpoints


def get_phe_midpoints(phe_coords: Coordinates) -> Midpoints:
    return _get_aromatic_midpoints(phe_coords, DICT_ATOMS_PHE)


def get_tyr_midpoints(tyr_coords: Coordinates) -> Midpoints:
    return _get_aromatic_midpoints(tyr_coords, DICT_ATOMS_TYR)


def get_trp_midpoints(trp_coords: Coordinates) -> Midpoints:
    return _get_aromatic_midpoints(trp_coords, DICT_ATOMS_TRP)
