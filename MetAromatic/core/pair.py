from logging import getLogger
from typing import Optional, List
from typing import Dict, Union
from .helpers import (
    filegetter,
    preprocessing,
    get_aromatic_midpoints,
    get_lone_pairs,
    distance_angular
)
from .helpers.consts import (
    EXIT_FAILURE,
    EXIT_SUCCESS,
    T
)
from numpy import ndarray

MAXIMUM_CUTOFF_ANGLE = 360.00


class FeatureSpace:

    PDB_CODE: str = None
    CUTOFF_DIST: float = None
    CUTOFF_ANGLE: float = None
    CHAIN: str = None
    MODEL: str = None

    RAW_DATA: Optional[List[str]] = []
    FIRST_MODEL: Optional[List[str]] = []

    COORDS_MET: Optional[List[List[str]]] = []
    COORDS_PHE: Optional[List[List[str]]] = []
    COORDS_TYR: Optional[List[List[str]]] = []
    COORDS_TRP: Optional[List[List[str]]] = []

    LONE_PAIRS_MET: Optional[List[Dict[str, ndarray]]] = []
    MIDPOINTS_PHE: Optional[List[List[Union[str, ndarray]]]] = []
    MIDPOINTS_TYR: Optional[List[List[Union[str, ndarray]]]] = []
    MIDPOINTS_TRP: Optional[List[List[Union[str, ndarray]]]] = []

    INTERACTIONS: Optional[List[Dict[str, Union[int, float, str]]]] = []


class MetAromatic:

    log = getLogger('met-aromatic')

    def __init__(self: T, cutoff_distance: float, cutoff_angle: float, chain: str, model: str) -> T:

        self.cutoff_distance = cutoff_distance
        self.cutoff_angle = cutoff_angle
        self.chain = chain
        self.model = model

        self.f = None
        self.results = None

    def check_invalid_cutoff_distance(self: T) -> bool:

        self.log.info('Validating cutoff distance')

        if self.cutoff_distance <= 0:

            self.log.error('Invalid cutoff distance. Cutoff distance must exceed 0 Angstroms')
            self.results['exit_status'] = "Invalid cutoff distance"
            self.results['exit_code'] = EXIT_FAILURE
            return False

        return True

    def check_invalid_cutoff_angle(self: T) -> bool:

        self.log.info('Validating cutoff angle')

        if (self.cutoff_angle < 0) or (self.cutoff_angle > MAXIMUM_CUTOFF_ANGLE):
            self.log.error('Invalid cutoff angle. Cutoff angle must be between 0 and %i degrees', MAXIMUM_CUTOFF_ANGLE)
            self.results['exit_status'] = "Invalid cutoff angle"
            self.results['exit_code'] = EXIT_FAILURE
            return False

        return True

    def fetch_pdb_file(self: T) -> bool:

        self.log.info('Fetching PDB file')

        file_from_pdb = filegetter.PDBFileGetter(self.results['_id'])

        filepath = file_from_pdb.fetch_entry_from_pdb()
        if not filepath:
            self.log.error('Invalid PDB file. Entry possibly does not exist')
            self.results['exit_status'] = "Invalid PDB file"
            self.results['exit_code'] = EXIT_FAILURE
            return False

        self.f.RAW_DATA = preprocessing.get_raw_data_from_file(filepath)

        if not file_from_pdb.remove_entry():
            self.log.error('Could not remove PDB file')
            self.results['exit_status'] = "Could not remove PDB file"
            self.results['exit_code'] = EXIT_FAILURE
            return False

        return True

    def get_first_model(self: T) -> bool:

        self.log.info('Stripping feature space down to only first model')

        self.f.FIRST_MODEL = preprocessing.get_first_model_from_raw_data(self.f.RAW_DATA)

        if len(self.f.FIRST_MODEL) == 0:
            self.log.error('No data for first model')
            self.results['exit_status'] = "No first model data"
            self.results['exit_code'] = EXIT_FAILURE
            return False

        return True

    def get_met_coordinates(self: T) -> bool:

        self.log.info('Isolating MET coordinates from feature space')

        self.f.COORDS_MET = preprocessing.get_relevant_met_coordinates(
            self.f.FIRST_MODEL, self.chain
        )

        if len(self.f.COORDS_MET) == 0:
            self.results['exit_status'] = "No MET residues"
            self.results['exit_code'] = EXIT_FAILURE
            return False

        return True

    def get_phe_coordinates(self: T) -> None:

        self.log.info('Isolating PHE coordinates from feature space')

        self.f.COORDS_PHE = preprocessing.get_relevant_phe_coordinates(
            self.f.FIRST_MODEL, self.chain
        )

    def get_tyr_coordinates(self: T) -> None:

        self.log.info('Isolating TYR coordinates from feature space')

        self.f.COORDS_TYR = preprocessing.get_relevant_tyr_coordinates(
            self.f.FIRST_MODEL, self.chain
        )

    def get_trp_coordinates(self: T) -> None:

        self.log.info('Isolating TRP coordinates from feature space')

        self.f.COORDS_TRP = preprocessing.get_relevant_trp_coordinates(
            self.f.FIRST_MODEL, self.chain
        )

    def check_if_not_coordinates(self: T) -> bool:

        self.log.info('Ensuring that at least one aromatic residue exists in feature space')

        if not any([self.f.COORDS_PHE, self.f.COORDS_TYR, self.f.COORDS_TRP]):
            self.log.error('No aromatic residues in feature space')
            self.results['exit_status'] = "No PHE/TYR/TRP residues"
            self.results['exit_code'] = EXIT_FAILURE
            return False

        return True

    def get_met_lone_pairs(self: T) -> bool:

        self.log.info('Computing MET lone pair positions using "%s" model', self.model)

        self.f.LONE_PAIRS_MET = get_lone_pairs.get_lone_pairs(
            self.f.COORDS_MET, self.model
        )

        if not self.f.LONE_PAIRS_MET:
            self.log.error('Invalid model "%s"', self.model)
            self.results['exit_status'] = "Invalid model"
            self.results['exit_code'] = EXIT_FAILURE
            return False

        return True

    def get_midpoints(self: T) -> None:

        self.log.info('Computing midpoints between PHE aromatic carbon atoms')

        self.f.MIDPOINTS_PHE = get_aromatic_midpoints.get_phe_midpoints(
            self.f.COORDS_PHE
        )

        self.log.info('Computing midpoints between TYR aromatic carbon atoms')

        self.f.MIDPOINTS_TYR = get_aromatic_midpoints.get_tyr_midpoints(
            self.f.COORDS_TYR
        )

        self.log.info('Computing midpoints between TRP aromatic carbon atoms')

        self.f.MIDPOINTS_TRP = get_aromatic_midpoints.get_trp_midpoints(
            self.f.COORDS_TRP
        )

    def get_interactions(self: T) -> bool:

        self.log.info('Finding pairs meeting Met-aromatic algorithm criteria in feature space')

        self.f.INTERACTIONS = distance_angular.apply_distance_angular_condition(
            self.f.MIDPOINTS_PHE + self.f.MIDPOINTS_TYR + self.f.MIDPOINTS_TRP,
            self.f.LONE_PAIRS_MET,
            self.cutoff_distance,
            self.cutoff_angle
        )

        if len(self.f.INTERACTIONS) == 0:
            self.log.error('Found no Met-aromatic interactions')
            self.results['exit_status'] = "No interactions"
            self.results['exit_code'] = EXIT_FAILURE
            return False

        self.results['exit_status'] = "Success"
        self.results['results'] = self.f.INTERACTIONS
        return True

    def get_met_aromatic_interactions(self: T, code: str) -> dict:

        self.log.info('Getting Met-aromatic interactions for PDB entry %s', code)

        self.f = FeatureSpace()

        self.f.PDB_CODE = code
        self.f.CUTOFF_DIST = self.cutoff_distance
        self.f.CUTOFF_ANGLE = self.cutoff_angle
        self.f.CHAIN = self.chain
        self.f.MODEL = self.model

        self.results = {
            '_id': code,
            'exit_code': EXIT_SUCCESS,
            'exit_status': None,
            'results': None
        }

        if not self.check_invalid_cutoff_distance():
            return self.results

        if not self.check_invalid_cutoff_angle():
            return self.results

        if not self.fetch_pdb_file():
            return self.results

        if not self.get_first_model():
            return self.results

        if not self.get_met_coordinates():
            return self.results

        self.get_phe_coordinates()
        self.get_tyr_coordinates()
        self.get_trp_coordinates()

        if not self.check_if_not_coordinates():
            return self.results

        if not self.get_met_lone_pairs():
            return self.results

        self.get_midpoints()

        if not self.get_interactions():
            return self.results

        return self.results
