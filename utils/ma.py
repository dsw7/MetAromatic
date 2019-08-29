# Written by David Weber
# dsw7@sfu.ca

"""
A low level implementation of the Met-Aromatic algorithm. I wrote this mainly
as an alternative to the more high level Pandas/BioPython implementation
of the algorithm. Here I mostly use built in libraries. This script would
be well suited for use in large mining jobs as the main function can be
imported into a separate workspace.
"""

# ------------------------------------------------------------------------------

from filegetter import PDBFile
from urllib.error import URLError
from re import search
from itertools import groupby
from operator import itemgetter
from utils import get_hexagon_midpoints
from utils import LonePairs
from utils import RodriguesMethod
from utils import vector_angle
from numpy import array
from numpy.linalg import norm


class MetAromaticConstants:
    ATOMS_MET = r'CE|SD|CG'
    ATOMS_TYR = r'CD1|CE1|CZ|CG|CD2|CE2'
    ATOMS_TRP = r'CD2|CE3|CZ2|CH2|CZ3|CE2'
    ATOMS_PHE = r'CD1|CE1|CZ|CG|CD2|CE2'
    IDX_ATOM = 0
    IDX_CHAIN = 4
    IDX_AA = 3
    IDX_ATM_LABEL = 2

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


class MetAromatic(MetAromaticConstants):
    def __init__(self, code, chain="A", cutoff=6.0, angle=109.5, model="cp"):
        self.code = code
        self.chain = chain.upper()
        self.cutoff = cutoff
        self.angle = angle
        self.model = model
        self.pdb_file_object = PDBFile(self.code)
        self.data = self._get_data_from_pdb()

    def _get_data_from_pdb(self, *args):
        file = self.pdb_file_object.fetch_from_pdb()
        data = []
        for line in open(file, 'r'):
            data.append(line)
        self.pdb_file_object.clear()
        return data

    def get_ec_classifier(self, *args):
        for line in self.data:
            if search(r"(?=.*COMPND )(?=.* EC:)", line):
                return line.split()[-1].strip(';')
            else:
                pass
            
    def get_organism(self, *args):
        lines = [line.split() for line in self.data]
        lines = [line for line in lines if 'SOURCE' in line]  # TODO regex this
        lines = [line for line in lines if 'ORGANISM_SCIENTIFIC:' in line]
        
        organism = []
        for item in lines:
            idx = item.index('ORGANISM_SCIENTIFIC:')
            out_str = '{} ' * len(item[idx + 1:])
            organism.append(out_str.format(*item[idx + 1:]))
            
        return organism

    def get_first_model(self, *args):
        # split downstream as get_ec_classifier() requires unsplit strings
        split, model = [line.split() for line in self.data], []
        for line in split:
            if line[self.IDX_ATOM] != 'ENDMDL':
                model.append(line)
            else:
                break
        return model

    def get_atoms(self, *args):
        model = self.get_first_model(self)
        return [line for line in model if line[self.IDX_ATOM] == 'ATOM']

    def get_chain(self, *args):
        atoms = self.get_atoms(self)
        return [line for line in atoms if line[self.IDX_CHAIN] == self.chain]

    def extract_aromatics(self, *args):
        atoms = self.get_chain(self)
        data_phe = [line for line in atoms if line[self.IDX_AA] == 'PHE']
        data_tyr = [line for line in atoms if line[self.IDX_AA] == 'TYR']
        data_trp = [line for line in atoms if line[self.IDX_AA] == 'TRP']
        return data_phe, data_trp, data_tyr

    def extract_methionines(self, *args):
        atoms = self.get_chain(self)
        return [line for line in atoms if line[self.IDX_AA] == 'MET']

    def cleanup_aromatics(self, *args):
        data_phe, data_trp, data_tyr = self.extract_aromatics(self)
        data_phe = [line for line in data_phe if search(self.ATOMS_PHE, line[self.IDX_ATM_LABEL]) != None]
        data_tyr = [line for line in data_tyr if search(self.ATOMS_TYR, line[self.IDX_ATM_LABEL]) != None]
        data_trp = [line for line in data_trp if search(self.ATOMS_TRP, line[self.IDX_ATM_LABEL]) != None]
        return data_phe, data_trp, data_tyr

    def cleanup_methionines(self, *args):
        data_met = self.extract_methionines(self)
        return [line for line in data_met if search(self.ATOMS_MET, line[self.IDX_ATM_LABEL]) != None]

    def get_midpoints_from_aromatic(self, *args):
        data_phe, data_tyr, data_trp = self.cleanup_aromatics(self)
        aromatics = data_phe + data_tyr + data_trp

        # need to group prior to getting midpoints
        aromatics = [list(group) for _, group in groupby(aromatics, lambda entry: entry[5])]

        # get midpoints
        midpoints = []
        for grouped in aromatics:
            # map unique values to atomic label keys
            for row in grouped:
                if row[3] == 'PHE':
                    row[2] = self.DICT_ATOMS_PHE.get(row[2])
                elif row[3] == 'TYR':
                    row[2] = self.DICT_ATOMS_TYR.get(row[2])
                else:
                    row[2] = self.DICT_ATOMS_TRP.get(row[2])

            # then sort based on these values which are just A, B, C, D, E, F
            ordered = sorted(grouped, key=itemgetter(2))

            # isolate x, y, z
            x = [float(i[6]) for i in ordered]
            y = [float(i[7]) for i in ordered]
            z = [float(i[8]) for i in ordered]

            # get hexagon midpoints
            x_mid, y_mid, z_mid = get_hexagon_midpoints(x, y, z)

            for a, b, c in zip(x_mid, y_mid, z_mid):
                midpoints.append([ordered[0][5], ordered[0][3], array([a, b, c])])

        return midpoints

    def met_aromatic(self):
        data_met = self.cleanup_methionines(self)
        midpoints = self.get_midpoints_from_aromatic(self)

        end_result = []

        # apply distance and angular conditions
        for key, grouped_met in groupby(data_met, lambda entry: entry[5]):
            # guarantees the order of methionine data
            ord_met = sorted(list(grouped_met), key=itemgetter(2))

            CE = array(ord_met[0][6:9]).astype(float)
            CG = array(ord_met[1][6:9]).astype(float)
            SD = array(ord_met[2][6:9]).astype(float)

            if self.model == 'cp':
                object_lonepairs = LonePairs(CG, SD, CE)
            elif self.model == 'rm':
                object_lonepairs = RodriguesMethod(CG, SD, CE)
            else:
                raise ValueError('Valid models are: cp, rm')

            vector_a = object_lonepairs.vector_a()
            vector_g = object_lonepairs.vector_g()

            for row in midpoints:
                vector_v = row[2] - SD  # mapping to origin of SD
                norm_v = norm(vector_v)
                if norm_v <= self.cutoff:  # distance condition
                    met_theta = vector_angle(vector_v, vector_a)
                    met_phi = vector_angle(vector_v, vector_g)
                    if met_theta <= self.angle or met_phi <= self.angle:  # angular condition
                        end_result.append([row[1], row[0], ord_met[0][3], ord_met[0][5], norm_v, met_theta, met_phi])
                    else:
                        continue
                else:
                    continue

        return end_result
