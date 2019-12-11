# Written by David Weber
# dsw7@sfu.ca

"""
A low level implementation of the Met-Aromatic algorithm. I wrote this mainly
as an alternative to the more high level Pandas/BioPython implementation
of the algorithm. Here I mostly use built in libraries. This script would
be well suited for use in large mining jobs as the main function can be
imported into a separate workspace.
"""

# -----------------------------------------------------------------------------
# Dependencies
# -----------------------------------------------------------------------------
from re import search, match
from copy import deepcopy
from itertools import groupby
from operator import itemgetter
from numpy import array
from numpy.linalg import norm
from networkx import Graph, connected_components
from filegetter import PDBFile
from linear_algebraic_helpers import get_hexagon_midpoints
from linear_algebraic_helpers import LonePairs
from linear_algebraic_helpers import RodriguesMethod
from linear_algebraic_helpers import vector_angle


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
ATOMS_MET = r'CE|SD|CG'
ATOMS_TYR = r'CD1|CE1|CZ|CG|CD2|CE2'
ATOMS_TRP = r'CD2|CE3|CZ2|CH2|CZ3|CE2'
ATOMS_PHE = r'CD1|CE1|CZ|CG|CD2|CE2'

PATTERN_MET = r'(ATOM.*({})\s*MET\s*A\s*)'.format(ATOMS_MET)   # TODO: replace hard regex for A chain with variable
PATTERN_PHE = r'(ATOM.*({})\s*PHE\s*A\s*)'.format(ATOMS_PHE)   # TODO: replace hard regex for A chain with variable   
PATTERN_TYR = r'(ATOM.*({})\s*TYR\s*A\s*)'.format(ATOMS_TYR)   # TODO: replace hard regex for A chain with variable
PATTERN_TRP = r'(ATOM.*({})\s*TRP\s*A\s*)'.format(ATOMS_TRP)   # TODO: replace hard regex for A chain with variable

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


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def get_aromatic_midpoints(aromatics, keys):
    # group prior to getting midpoints
    aromatics = [list(group) for _, group in groupby(aromatics, lambda entry: entry[5])]

    midpoints = []
    for grouped in deepcopy(aromatics):  # fix for self.phenylalanines A, B, C bug
        for row in grouped:  # map unique values to atomic label keys
            row[2] = keys.get(row[2])

        # sort based on these values which are just A, B, C, D, E, F
        ordered = sorted(grouped, key=itemgetter(2))
        x = [float(i[6]) for i in ordered]
        y = [float(i[7]) for i in ordered]
        z = [float(i[8]) for i in ordered]
        x_mid, y_mid, z_mid = get_hexagon_midpoints(x, y, z)

        for a, b, c in zip(x_mid, y_mid, z_mid):
            midpoints.append([ordered[0][5], ordered[0][3], array([a, b, c])])

    return midpoints


# -----------------------------------------------------------------------------
# The master class
# -----------------------------------------------------------------------------
class MetAromatic:
    def __init__(self, code, chain="A", cutoff=6.0, angle=109.5, model="cp"):
        self.code = code
        self.chain = chain.upper()  # XXX chain not used anywhere
        self.cutoff = cutoff
        self.angle = angle
        self.model = model
        self.first_model = None
        self.methionine_coords = None
        self.phenylalanine_coords = None
        self.tyrosine_coords = None
        self.tryptophan_coords = None
        self.midpoints_phe = None
        self.midpoints_tyr = None
        self.midpoints_trp = None
        self.midpoints = None
        self.pairs = None
        self.preprocessed_met_data = None
        self.lone_pairs = None

        pdb_file_object = PDBFile(self.code)
        file_from_pdb = pdb_file_object.fetch_from_pdb()
        self.first_model = []
        for line in open(file_from_pdb, 'r'):
            if 'ENDMDL' not in line:
                self.first_model.append(line)
            else:
                break
        pdb_file_object.clear()

    # ------------------------------------------------------
    # Other helpers
    # ------------------------------------------------------
    def get_ec_classifier(self):
        """ COMPND   5 EC: 6.1.1.13; -> 6.1.1.13 """
        for line in self.first_model:
            if search(r'COMPND.*EC:', line):
                return search(r'(?<=: )(.*)(?=;)', line).group(0)

    def get_protein_identity(self):
        """ COMPND   2 MOLECULE: D-ALANINE; -> D-ALANINE """
        for line in self.first_model:
            if search(r'COMPND.*MOLECULE:', line):
                return search('(?<=: ).*?(?=;|\n)', line).group(0)

    def get_organism(self):
        """ SOURCE   2 ORGANISM_SCIENTIFIC: B. SUBTILIS; -> B. SUBTILIS """
        for line in self.first_model:
            if search(r'SOURCE.*ORGANISM_SCIENTIFIC:', line):
                return search('(?<=: ).*?(?=;|\n)', line).group(0)

    def bridging_interactions(self, n=3):
        """
        Note that this function is slightly different from previous studies.
        Here the MET node is included as part of the chain. This means that
        for a 2-bridge we actually have to set n = 3: i.e. ARO-MET-ARO. For a
        3-bridge we have to set n = 4, etc.
        """
        joined = [(''.join(pair[0:2]), ''.join(pair[2:4])) for pair in self.pairs]
        joined = list(set(joined))
        nx_graph = Graph()
        nx_graph.add_edges_from(joined)
        bridges = list(connected_components(nx_graph))
        bridges = [bridge for bridge in bridges if len(bridge) == n]
        return bridges  # note that inverse bridges (MET-ARO-MET) not removed!

    # ------------------------------------------------------
    # Regex core Met-aromatic data
    # ------------------------------------------------------
    def get_relevant_coordinates_from_met(self):
        self.methionine_coords = [line.split() for line in self.first_model \
                if match(PATTERN_MET, line)]

    def get_relevant_coordinates_from_phe(self):
        self.phenylalanine_coords = [line.split() for line in self.first_model \
                if match(PATTERN_PHE, line)]

    def get_relevant_coordinates_from_tyr(self):
        self.tyrosine_coords = [line.split() for line in self.first_model \
                if match(PATTERN_TYR, line)]

    def get_relevant_coordinates_from_trp(self):
        self.tryptophan_coords = [line.split() for line in self.first_model \
                if match(PATTERN_TRP, line)]

    # ------------------------------------------------------
    # Preprocessing methods
    # ------------------------------------------------------
    def get_phe_midpoints(self):
        self.midpoints_phe = get_aromatic_midpoints(self.phenylalanine_coords, DICT_ATOMS_PHE)

    def get_tyr_midpoints(self):
        self.midpoints_tyr = get_aromatic_midpoints(self.tyrosine_coords, DICT_ATOMS_TYR)

    def get_trp_midpoints(self):
        self.midpoints_trp = get_aromatic_midpoints(self.tryptophan_coords, DICT_ATOMS_TRP)

    def preprocess_met_data(self):
        self.preprocessed_met_data = []
        for _, met_grouped in groupby(self.methionine_coords, lambda entry: entry[5]):
            met_ordered = sorted(list(met_grouped), key=itemgetter(2))
            dict_met = {}
            dict_met['coords_ce'] = array(met_ordered[0][6:9]).astype(float)
            dict_met['coords_cg'] = array(met_ordered[1][6:9]).astype(float)
            dict_met['coords_sd'] = array(met_ordered[2][6:9]).astype(float)
            dict_met['position'] = met_ordered[0][5]
            self.preprocessed_met_data.append(dict_met)

    def get_lone_pairs(self):
        self.lone_pairs = []
        for dict_met in self.preprocessed_met_data:
            dict_lone_pairs = {}
            coords_cg = dict_met['coords_cg']
            coords_ce = dict_met['coords_ce']
            coords_sd = dict_met['coords_sd']

            if self.model == 'rm':
                object_lonepairs = RodriguesMethod(coords_cg, coords_sd, coords_ce)
            else:
                object_lonepairs = LonePairs(coords_cg, coords_sd, coords_ce)

            dict_lone_pairs['vector_a'] = object_lonepairs.vector_a()
            dict_lone_pairs['vector_g'] = object_lonepairs.vector_g()
            dict_lone_pairs['coords_sd'] = dict_met['coords_sd']
            dict_lone_pairs['position'] = dict_met['position']
            self.lone_pairs.append(dict_lone_pairs)

    # ------------------------------------------------------
    # Postprocessing methods
    # ------------------------------------------------------
    def met_constructor(self):
        self.get_relevant_coordinates_from_met()
        self.preprocess_met_data()
        self.get_lone_pairs()

    def phe_constructor(self):
        self.get_relevant_coordinates_from_phe()
        self.get_phe_midpoints()

    def tyr_constructor(self):
        self.get_relevant_coordinates_from_tyr()
        self.get_tyr_midpoints()

    def trp_constructor(self):
        self.get_relevant_coordinates_from_trp()
        self.get_trp_midpoints()

    def met_aromatic(self):
        self.met_constructor()
        self.phe_constructor()
        self.tyr_constructor()
        self.trp_constructor()
        self.pairs = []

        for dict_met in self.lone_pairs:
            for midpoints in self.midpoints_phe + self.midpoints_tyr + self.midpoints_trp:
                vector_v = midpoints[2] - dict_met['coords_sd']
                norm_v = norm(vector_v)
                if norm_v <= self.cutoff:  # distance condition
                    met_theta = vector_angle(vector_v, dict_met['vector_a'])
                    met_phi = vector_angle(vector_v, dict_met['vector_g'])
                    if met_theta <= self.angle or met_phi <= self.angle:  # angular condition
                        self.pairs.append([midpoints[1], midpoints[0], 'MET',
                                           dict_met['position'], norm_v, met_theta, met_phi])
        return self.pairs


# -----------------------------------------------------------------------------
# Examples
# -----------------------------------------------------------------------------
def example_get_ec_classifier(code):
    obj = MetAromatic(code=code)
    return obj.get_ec_classifier()

def example_get_protein_identity(code):
    obj = MetAromatic(code=code)
    return obj.get_protein_identity()

def example_get_organism(code):
    obj = MetAromatic(code=code)
    return obj.get_organism()

def example_get_bridges(code):
    obj = MetAromatic(code=code)
    obj.met_aromatic()
    # have to use n + 1 to include met
    # have to use in clause because ma returns
    # multiple bridges (including inverts)
    return obj.bridging_interactions(n=4)
