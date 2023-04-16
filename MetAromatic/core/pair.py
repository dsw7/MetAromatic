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
from core.helpers.consts import T
from core.helpers.get_aromatic_midpoints import get_phe_midpoints
from core.helpers.get_aromatic_midpoints import get_trp_midpoints
from core.helpers.get_aromatic_midpoints import get_tyr_midpoints
from core.helpers.lone_pair_interpolators import RodriguesMethod, CrossProductMethod

TMPDIR = gettempdir()

def vector_angle(u: ndarray, v: ndarray) -> float:

    dot_prod = dot(u, v)
    prod_mag = linalg.norm(v) * linalg.norm(u)

    return degrees(arccos(dot_prod / prod_mag))


@dataclass
class FeatureSpace:

    PDB_CODE: str = None
    CUTOFF_DIST: float = None
    CUTOFF_ANGLE: float = None
    CHAIN: str = None
    MODEL: str = None

    RAW_DATA: Optional[List[str]] = field(default_factory=list)
    FIRST_MODEL: Optional[List[str]] = field(default_factory=list)

    COORDS_MET: Optional[List[List[str]]] = field(default_factory=list)
    COORDS_PHE: Optional[List[List[str]]] = field(default_factory=list)
    COORDS_TYR: Optional[List[List[str]]] = field(default_factory=list)
    COORDS_TRP: Optional[List[List[str]]] = field(default_factory=list)

    LONE_PAIRS_MET: Optional[List[Dict[str, ndarray]]] = field(default_factory=list)
    MIDPOINTS_PHE: Optional[List[List[Union[str, ndarray]]]] = field(default_factory=list)
    MIDPOINTS_TYR: Optional[List[List[Union[str, ndarray]]]] = field(default_factory=list)
    MIDPOINTS_TRP: Optional[List[List[Union[str, ndarray]]]] = field(default_factory=list)

    INTERACTIONS: Optional[List[Dict[str, Union[int, float, str]]]] = field(default_factory=list)

    OK: bool = True
    STATUS: str = 'Success'


class MetAromatic:

    log = getLogger('met-aromatic')

    def __init__(self: T, cutoff_distance: float, cutoff_angle: float, chain: str, model: str) -> T:

        self.cutoff_distance = cutoff_distance
        self.cutoff_angle = cutoff_angle
        self.chain = chain
        self.model = model

        self.f = None

    def fetch_pdb_file(self: T) -> bool:

        self.log.info('Fetching PDB file "%s"', self.f.PDB_CODE)

        code = self.f.PDB_CODE.lower()

        ent_gz = f'pdb{code}.ent.gz'
        ftp_url = f'ftp://ftp.wwpdb.org/pub/pdb/data/structures/divided/pdb/{code[1:3]}/{ent_gz}'

        self.log.info('Accessing URL: "%s"', ftp_url)

        with NamedTemporaryFile(dir=TMPDIR) as f:

            try:
                urlcleanup()
                urlretrieve(ftp_url, f.name)
            except URLError:
                self.log.error('Invalid PDB entry. Entry possibly does not exist')

                self.f.STATUS = "Invalid PDB entry"
                self.f.OK = False
                return False

            with gz_open(f.name, 'rt') as gz:
                for line in gz:
                    self.f.RAW_DATA.append(line)

        return True

    def get_first_model(self: T) -> None:

        self.log.info('Stripping feature space down to only first model')

        for line in self.f.RAW_DATA:
            if 'ENDMDL' in line:
                break

            self.f.FIRST_MODEL.append(line)

    def get_met_coordinates(self: T) -> bool:

        self.log.info('Isolating MET coordinates from feature space')

        pattern = compile(rf'(ATOM.*(CE|SD|CG)\s+MET\s+{self.chain}\s)')

        for line in self.f.FIRST_MODEL:
            if match(pattern, line):
                self.f.COORDS_MET.append(line.split()[:9])

        if len(self.f.COORDS_MET) == 0:
            self.f.STATUS = "No MET residues"
            self.f.OK = False
            return False

        return True

    def get_phe_coordinates(self: T) -> None:

        self.log.info('Isolating PHE coordinates from feature space')

        pattern = compile(rf'(ATOM.*(CD1|CE1|CZ|CG|CD2|CE2)\s+PHE\s+{self.chain}\s)')

        for line in self.f.FIRST_MODEL:
            if match(pattern, line):
                self.f.COORDS_PHE.append(line.split()[:9])

    def get_tyr_coordinates(self: T) -> None:

        self.log.info('Isolating TYR coordinates from feature space')

        pattern = compile(rf'(ATOM.*(CD1|CE1|CZ|CG|CD2|CE2)\s+TYR\s+{self.chain}\s)')

        for line in self.f.FIRST_MODEL:
            if match(pattern, line):
                self.f.COORDS_TYR.append(line.split()[:9])

    def get_trp_coordinates(self: T) -> None:

        self.log.info('Isolating TRP coordinates from feature space')

        pattern = compile(rf'(ATOM.*(CD2|CE3|CZ2|CH2|CZ3|CE2)\s+TRP\s+{self.chain}\s)')

        for line in self.f.FIRST_MODEL:
            if match(pattern, line):
                self.f.COORDS_TRP.append(line.split()[:9])

    def check_if_not_coordinates(self: T) -> bool:

        self.log.info('Ensuring that at least one aromatic residue exists in feature space')

        if not any([self.f.COORDS_PHE, self.f.COORDS_TYR, self.f.COORDS_TRP]):
            self.log.error('No aromatic residues in feature space')
            self.f.STATUS = "No PHE/TYR/TRP residues"
            self.f.OK = False
            return False

        return True

    def get_met_lone_pairs(self: T) -> None:

        self.log.info('Computing MET lone pair positions using "%s" model', self.model)

        if self.model == 'cp':
            model_lp = CrossProductMethod
        else:
            model_lp = RodriguesMethod

        for position, groups in groupby(self.f.COORDS_MET, lambda entry: entry[5]):
            ordered = sorted(list(groups), key=itemgetter(2))

            coords_ce = array(ordered[0][6:9]).astype(float)
            coords_cg = array(ordered[1][6:9]).astype(float)
            coords_sd = array(ordered[2][6:9]).astype(float)

            lp = model_lp(coords_cg, coords_sd, coords_ce)

            self.f.LONE_PAIRS_MET.append({
                'vector_a': lp.get_vector_a(),
                'vector_g': lp.get_vector_g(),
                'coords_sd': coords_sd,
                'position': position
            })

    def get_midpoints(self: T) -> None:

        self.log.info('Computing midpoints between PHE aromatic carbon atoms')
        self.f.MIDPOINTS_PHE = get_phe_midpoints(self.f.COORDS_PHE)

        self.log.info('Computing midpoints between TYR aromatic carbon atoms')
        self.f.MIDPOINTS_TYR = get_tyr_midpoints(self.f.COORDS_TYR)

        self.log.info('Computing midpoints between TRP aromatic carbon atoms')
        self.f.MIDPOINTS_TRP = get_trp_midpoints(self.f.COORDS_TRP)

    def apply_met_aromatic_criteria(self: T) -> None:

        self.log.info('Finding pairs meeting Met-aromatic algorithm criteria in feature space')

        for lone_pair in self.f.LONE_PAIRS_MET:
            for midpoint in self.f.MIDPOINTS_PHE + self.f.MIDPOINTS_TYR + self.f.MIDPOINTS_TRP:

                v = midpoint[2] - lone_pair['coords_sd']
                norm_v = linalg.norm(v)

                if norm_v > self.cutoff_distance:
                    continue

                met_theta_angle = vector_angle(v, lone_pair['vector_a'])
                met_phi_angle = vector_angle(v, lone_pair['vector_g'])

                if (met_theta_angle > self.cutoff_angle) and (met_phi_angle > self.cutoff_angle):
                    continue

                self.f.INTERACTIONS.append({
                    'aromatic_residue': midpoint[1],
                    'aromatic_position': int(midpoint[0]),
                    'methionine_position': int(lone_pair['position']),
                    'norm': round(norm_v, 3),
                    'met_theta_angle': round(met_theta_angle, 3),
                    'met_phi_angle': round(met_phi_angle, 3)
                })

        if len(self.f.INTERACTIONS) == 0:
            self.log.error('Found no Met-aromatic interactions')
            self.f.STATUS = "No interactions"
            self.f.OK = False

    def get_met_aromatic_interactions(self: T, code: str) -> FeatureSpace:

        self.log.info('Getting Met-aromatic interactions for PDB entry %s', code)

        self.f = FeatureSpace()

        self.f.PDB_CODE = code
        self.f.CUTOFF_DIST = self.cutoff_distance
        self.f.CUTOFF_ANGLE = self.cutoff_angle
        self.f.CHAIN = self.chain
        self.f.MODEL = self.model

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
