from dataclasses import dataclass, field
from gzip import open as gz_open
from itertools import groupby
from logging import getLogger
from operator import itemgetter
from re import match, compile
from tempfile import gettempdir, NamedTemporaryFile
from typing import Dict, Union
from typing import Optional, List
from urllib.error import URLError
from urllib.request import urlretrieve, urlcleanup

from numpy import ndarray, array, dot, linalg, degrees, arccos
from MetAromatic.consts import T
from MetAromatic.get_aromatic_midpoints import get_phe_midpoints
from MetAromatic.get_aromatic_midpoints import get_trp_midpoints
from MetAromatic.get_aromatic_midpoints import get_tyr_midpoints
from MetAromatic.lone_pair_interpolators import RodriguesMethod, CrossProductMethod

TMPDIR = gettempdir()

def vector_angle(u: ndarray, v: ndarray) -> float:

    dot_prod = dot(u, v)
    prod_mag = linalg.norm(v) * linalg.norm(u)

    return degrees(arccos(dot_prod / prod_mag))


@dataclass
class FeatureSpace:

    pdb_code: str = None
    cutoff_dist: float = None
    cutoff_angle: float = None
    chain: str = None
    model: str = None

    raw_data: Optional[List[str]] = field(default_factory=list)
    first_model: Optional[List[str]] = field(default_factory=list)

    coords_met: Optional[List[List[str]]] = field(default_factory=list)
    coords_phe: Optional[List[List[str]]] = field(default_factory=list)
    coords_tyr: Optional[List[List[str]]] = field(default_factory=list)
    coords_trp: Optional[List[List[str]]] = field(default_factory=list)

    lone_pairs_met: Optional[List[Dict[str, ndarray]]] = field(default_factory=list)
    midpoints_phe: Optional[List[List[Union[str, ndarray]]]] = field(default_factory=list)
    midpoints_tyr: Optional[List[List[Union[str, ndarray]]]] = field(default_factory=list)
    midpoints_trp: Optional[List[List[Union[str, ndarray]]]] = field(default_factory=list)

    interactions: Optional[List[Dict[str, Union[int, float, str]]]] = field(default_factory=list)

    OK: bool = True
    status: str = 'Success'


class MetAromatic:

    log = getLogger('met-aromatic')

    def __init__(self: T, cutoff_distance: float, cutoff_angle: float, chain: str, model: str) -> T:

        self.cutoff_distance = cutoff_distance
        self.cutoff_angle = cutoff_angle
        self.chain = chain
        self.model = model

        self.f = None

    def fetch_pdb_file(self: T) -> bool:

        self.log.debug('Fetching PDB file "%s"', self.f.pdb_code)

        code = self.f.pdb_code.lower()

        ent_gz = f'pdb{code}.ent.gz'
        ftp_url = f'ftp://ftp.wwpdb.org/pub/pdb/data/structures/divided/pdb/{code[1:3]}/{ent_gz}'

        self.log.debug('Accessing URL: "%s"', ftp_url)

        with NamedTemporaryFile(dir=TMPDIR) as f:

            try:
                urlcleanup()
                urlretrieve(ftp_url, f.name)
            except URLError:
                self.log.error('Invalid PDB entry "%s"', self.f.pdb_code)

                self.f.status = "Invalid PDB entry"
                self.f.OK = False
                return False

            with gz_open(f.name, 'rt') as gz:
                for line in gz:
                    self.f.raw_data.append(line)

        return True

    def get_first_model(self: T) -> None:

        self.log.debug('Stripping feature space down to only first model')

        for line in self.f.raw_data:
            if 'ENDMDL' in line:
                break

            self.f.first_model.append(line)

    def get_met_coordinates(self: T) -> bool:

        self.log.debug('Isolating MET coordinates from feature space')

        pattern = compile(rf'(ATOM.*(CE|SD|CG)\s+MET\s+{self.chain}\s)')

        for line in self.f.first_model:
            if match(pattern, line):
                self.f.coords_met.append(line.split()[:9])

        if len(self.f.coords_met) == 0:
            self.log.error('No methionine residues found for entry "%s"', self.f.pdb_code)

            self.f.status = "No MET residues"
            self.f.OK = False
            return False

        return True

    def get_phe_coordinates(self: T) -> None:

        self.log.debug('Isolating PHE coordinates from feature space')

        pattern = compile(rf'(ATOM.*(CD1|CE1|CZ|CG|CD2|CE2)\s+PHE\s+{self.chain}\s)')

        for line in self.f.first_model:
            if match(pattern, line):
                self.f.coords_phe.append(line.split()[:9])

    def get_tyr_coordinates(self: T) -> None:

        self.log.debug('Isolating TYR coordinates from feature space')

        pattern = compile(rf'(ATOM.*(CD1|CE1|CZ|CG|CD2|CE2)\s+TYR\s+{self.chain}\s)')

        for line in self.f.first_model:
            if match(pattern, line):
                self.f.coords_tyr.append(line.split()[:9])

    def get_trp_coordinates(self: T) -> None:

        self.log.debug('Isolating TRP coordinates from feature space')

        pattern = compile(rf'(ATOM.*(CD2|CE3|CZ2|CH2|CZ3|CE2)\s+TRP\s+{self.chain}\s)')

        for line in self.f.first_model:
            if match(pattern, line):
                self.f.coords_trp.append(line.split()[:9])

    def check_if_not_coordinates(self: T) -> bool:

        self.log.debug('Ensuring that at least one aromatic residue exists in feature space')

        if not any([self.f.coords_phe, self.f.coords_tyr, self.f.coords_trp]):
            self.log.error('No aromatic residues found for entry "%s"', self.f.pdb_code)
            self.f.status = "No PHE/TYR/TRP residues"
            self.f.OK = False
            return False

        return True

    def get_met_lone_pairs(self: T) -> None:

        self.log.debug('Computing MET lone pair positions using "%s" model', self.model)

        if self.model == 'cp':
            model_lp = CrossProductMethod
        else:
            model_lp = RodriguesMethod

        for position, groups in groupby(self.f.coords_met, lambda entry: entry[5]):
            ordered = sorted(list(groups), key=itemgetter(2))

            coords_ce = array(ordered[0][6:9]).astype(float)
            coords_cg = array(ordered[1][6:9]).astype(float)
            coords_sd = array(ordered[2][6:9]).astype(float)

            lp = model_lp(coords_cg, coords_sd, coords_ce)

            self.f.lone_pairs_met.append({
                'vector_a': lp.get_vector_a(),
                'vector_g': lp.get_vector_g(),
                'coords_sd': coords_sd,
                'position': position
            })

    def get_midpoints(self: T) -> None:

        self.log.debug('Computing midpoints between PHE aromatic carbon atoms')
        self.f.midpoints_phe = get_phe_midpoints(self.f.coords_phe)

        self.log.debug('Computing midpoints between TYR aromatic carbon atoms')
        self.f.midpoints_tyr = get_tyr_midpoints(self.f.coords_tyr)

        self.log.debug('Computing midpoints between TRP aromatic carbon atoms')
        self.f.midpoints_trp = get_trp_midpoints(self.f.coords_trp)

    def apply_met_aromatic_criteria(self: T) -> None:

        self.log.debug('Finding pairs meeting Met-aromatic algorithm criteria in feature space')

        midpoints = self.f.midpoints_phe + self.f.midpoints_tyr + self.f.midpoints_trp

        for lone_pair in self.f.lone_pairs_met:
            for midpoint in midpoints:

                v = midpoint[2] - lone_pair['coords_sd']
                norm_v = linalg.norm(v)

                if norm_v > self.cutoff_distance:
                    continue

                met_theta_angle = vector_angle(v, lone_pair['vector_a'])
                met_phi_angle = vector_angle(v, lone_pair['vector_g'])

                if (met_theta_angle > self.cutoff_angle) and (met_phi_angle > self.cutoff_angle):
                    continue

                self.f.interactions.append({
                    'aromatic_residue': midpoint[1],
                    'aromatic_position': int(midpoint[0]),
                    'methionine_position': int(lone_pair['position']),
                    'norm': round(norm_v, 3),
                    'met_theta_angle': round(met_theta_angle, 3),
                    'met_phi_angle': round(met_phi_angle, 3)
                })

        if len(self.f.interactions) == 0:
            self.log.error('Found no Met-aromatic interactions for entry "%s"', self.f.pdb_code)
            self.f.status = "No interactions"
            self.f.OK = False

    def get_met_aromatic_interactions(self: T, code: str) -> FeatureSpace:

        self.log.info('Getting Met-aromatic interactions for PDB entry %s', code)

        self.f = FeatureSpace()

        self.f.pdb_code = code
        self.f.cutoff_dist = self.cutoff_distance
        self.f.cutoff_angle = self.cutoff_angle
        self.f.chain = self.chain
        self.f.model = self.model

        if not self.fetch_pdb_file():
            return self.f

        self.get_first_model()

        if not self.get_met_coordinates():
            return self.f

        self.get_phe_coordinates()
        self.get_tyr_coordinates()
        self.get_trp_coordinates()

        if not self.check_if_not_coordinates():
            return self.f

        self.get_met_lone_pairs()
        self.get_midpoints()
        self.apply_met_aromatic_criteria()

        return self.f
