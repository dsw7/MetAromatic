from dataclasses import dataclass, field
from re import match, compile
from logging import getLogger
from typing import Optional, List
from typing import Dict, Union
from numpy import ndarray
from core.helpers.consts import T
from core.helpers.get_aromatic_midpoints import get_phe_midpoints
from core.helpers.get_aromatic_midpoints import get_tyr_midpoints
from core.helpers.get_aromatic_midpoints import get_trp_midpoints
from core.helpers import (
    filegetter,
    get_lone_pairs,
    distance_angular
)

MAXIMUM_CUTOFF_ANGLE = 360.00


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

    def check_invalid_cutoff_distance(self: T) -> bool:

        self.log.info('Validating cutoff distance')

        if self.cutoff_distance <= 0:

            self.log.error('Invalid cutoff distance. Cutoff distance must exceed 0 Angstroms')
            self.f.STATUS = "Invalid cutoff distance"
            self.f.OK = False
            return False

        return True

    def check_invalid_cutoff_angle(self: T) -> bool:

        self.log.info('Validating cutoff angle')

        if (self.cutoff_angle < 0) or (self.cutoff_angle > MAXIMUM_CUTOFF_ANGLE):
            self.log.error('Invalid cutoff angle. Cutoff angle must be between 0 and %i degrees', MAXIMUM_CUTOFF_ANGLE)
            self.f.STATUS = "Invalid cutoff angle"
            self.f.OK = False
            return False

        return True

    def fetch_pdb_file(self: T) -> bool:

        self.log.info('Fetching PDB file')

        file_handle = filegetter.PDBFileGetter(self.f.PDB_CODE)

        path_pdb_file = file_handle.fetch_entry_from_pdb()

        if path_pdb_file is None:
            self.log.error('Invalid PDB entry. Entry possibly does not exist')
            self.f.STATUS = "Invalid PDB entry"
            self.f.OK = False
            return False

        if not path_pdb_file.exists():
            self.log.error('Could not find PDB file "%s"', path_pdb_file)
            self.f.STATUS = 'PDB file does not exist'
            self.f.OK = False
            return False

        self.log.info('Loading data from PDB file "%s"', path_pdb_file)

        with path_pdb_file.open() as f:
            for line in f:
                self.f.RAW_DATA.append(line)

        file_handle.remove_entry()
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
        self.f.LONE_PAIRS_MET = get_lone_pairs.get_lone_pairs(self.f.COORDS_MET, self.model)

    def get_midpoints(self: T) -> None:

        self.log.info('Computing midpoints between PHE aromatic carbon atoms')
        self.f.MIDPOINTS_PHE = get_phe_midpoints(self.f.COORDS_PHE)

        self.log.info('Computing midpoints between TYR aromatic carbon atoms')
        self.f.MIDPOINTS_TYR = get_tyr_midpoints(self.f.COORDS_TYR)

        self.log.info('Computing midpoints between TRP aromatic carbon atoms')
        self.f.MIDPOINTS_TRP = get_trp_midpoints(self.f.COORDS_TRP)

    def get_interactions(self: T) -> None:

        self.log.info('Finding pairs meeting Met-aromatic algorithm criteria in feature space')

        self.f.INTERACTIONS = distance_angular.apply_distance_angular_condition(
            self.f.MIDPOINTS_PHE + self.f.MIDPOINTS_TYR + self.f.MIDPOINTS_TRP,
            self.f.LONE_PAIRS_MET,
            self.cutoff_distance,
            self.cutoff_angle
        )

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

        if not self.check_invalid_cutoff_distance():
            return self.f

        if not self.check_invalid_cutoff_angle():
            return self.f

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
        self.get_interactions()

        return self.f
