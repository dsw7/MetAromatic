from networkx import Graph, connected_components
from .primitives import (
    filegetter,
    preprocessing,
    get_aromatic_midpoints,
    get_lone_pairs,
    distance_angular
)
from .primitives.consts import (
    EXIT_FAILURE,
    EXIT_SUCCESS,
    MINIMUM_VERTICES,
    MINIMUM_CUTOFF_DIST,
    MINIMUM_CUTOFF_ANGLE,
    MAXIMUM_CUTOFF_ANGLE
)


class MetAromatic:

    def __init__(self, cutoff_distance: float, cutoff_angle: float, chain: str, model: str) -> None:
        self.cutoff_distance = cutoff_distance
        self.cutoff_angle = cutoff_angle
        self.chain = chain
        self.model = model

        self.results = None
        self.transport = {
            'raw_data': None,
            'first_model': None,
            'met_coordinates': None,
            'phe_coordinates': None,
            'tyr_coordinates': None,
            'trp_coordinates': None,
            'met_lone_pairs': None,
            'phe_midpoints': None,
            'tyr_midpoints': None,
            'trp_midpoints': None,
            'interactions': None
        }

    def check_invalid_cutoff_distance(self) -> bool:
        if self.cutoff_distance <= MINIMUM_CUTOFF_DIST:
            self.results['exit_status'] = "Invalid cutoff distance"
            self.results['exit_code'] = EXIT_FAILURE
            return False
        return True

    def check_invalid_cutoff_angle(self) -> bool:
        if (self.cutoff_angle < MINIMUM_CUTOFF_ANGLE) or (self.cutoff_angle > MAXIMUM_CUTOFF_ANGLE):
            self.results['exit_status'] = "Invalid cutoff angle"
            self.results['exit_code'] = EXIT_FAILURE
            return False
        return True

    def fetch_pdb_file(self) -> bool:
        file_from_pdb = filegetter.PDBFileGetter(self.results['_id'])

        filepath = file_from_pdb.fetch_entry_from_pdb()
        if not filepath:
            self.results['exit_status'] = "Invalid PDB file"
            self.results['exit_code'] = EXIT_FAILURE
            return False

        self.transport['raw_data'] = preprocessing.get_raw_data_from_file(filepath)

        if not file_from_pdb.remove_entry():
            self.results['exit_status'] = "Could not remove PDB file"
            self.results['exit_code'] = EXIT_FAILURE
            return False

        return True

    def get_first_model(self) -> bool:
        self.transport['first_model'] = preprocessing.get_first_model_from_raw_data(self.transport['raw_data'])

        if not self.transport['first_model']:
            self.results['exit_status'] = "No first model data"
            self.results['exit_code'] = EXIT_FAILURE
            return False

        return True

    def get_met_coordinates(self) -> bool:
        self.transport['met_coordinates'] = preprocessing.get_relevant_met_coordinates(
            self.transport['first_model'], self.chain
        )

        if not self.transport['met_coordinates']:
            self.results['exit_status'] = "No MET residues"
            self.results['exit_code'] = EXIT_FAILURE
            return False

        return True

    def get_phe_coordinates(self) -> None:
        self.transport['phe_coordinates'] = preprocessing.get_relevant_phe_coordinates(
            self.transport['first_model'], self.chain
        )

    def get_tyr_coordinates(self) -> None:
        self.transport['tyr_coordinates'] = preprocessing.get_relevant_tyr_coordinates(
            self.transport['first_model'], self.chain
        )

    def get_trp_coordinates(self) -> None:
        self.transport['trp_coordinates'] = preprocessing.get_relevant_trp_coordinates(
            self.transport['first_model'], self.chain
        )

    def check_if_not_coordinates(self) -> bool:
        if not any([self.transport['phe_coordinates'], self.transport['tyr_coordinates'], self.transport['phe_coordinates']]):
            self.results['exit_status'] = "No PHE/TYR/TRP residues"
            self.results['exit_code'] = EXIT_FAILURE
            return False

        return True

    def get_met_lone_pairs(self) -> bool:
        self.transport['met_lone_pairs'] = get_lone_pairs.get_lone_pairs(
            self.transport['met_coordinates'], self.model
        )

        if not self.transport['met_lone_pairs']:
            self.results['exit_status'] = "Invalid model"
            self.results['exit_code'] = EXIT_FAILURE
            return False

        return True

    def get_midpoints(self) -> None:
        self.transport['phe_midpoints'] = get_aromatic_midpoints.get_phe_midpoints(
            self.transport['phe_coordinates']
        )

        self.transport['tyr_midpoints'] = get_aromatic_midpoints.get_tyr_midpoints(
            self.transport['tyr_coordinates']
        )

        self.transport['trp_midpoints'] = get_aromatic_midpoints.get_trp_midpoints(
            self.transport['trp_coordinates']
        )

    def get_interactions(self) -> bool:

        self.transport['interactions'] = distance_angular.apply_distance_angular_condition(
            self.transport['phe_midpoints'] + self.transport['tyr_midpoints'] + self.transport['trp_midpoints'],
            self.transport['met_lone_pairs'],
            self.cutoff_distance,
            self.cutoff_angle
        )

        if not self.transport['interactions']:
            self.results['exit_status'] = "No interactions"
            self.results['exit_code'] = EXIT_FAILURE
            return False

        self.results['exit_status'] = "Success"
        self.results['results'] = self.transport['interactions']
        return True

    def get_met_aromatic_interactions(self, code: str) -> dict:

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


class GetBridgingInteraction(MetAromatic):

    def __init__(self, cutoff_distance: float, cutoff_angle: float, chain: str, model: str) -> None:
        MetAromatic.__init__(self, cutoff_distance, cutoff_angle, chain, model)

        self.results = None
        self.vertices = None
        self.code = None
        self.joined_pairs = set()
        self.bridges = None

    def check_minimum_vertices(self) -> bool:
        if self.vertices < MINIMUM_VERTICES:
            self.results['exit_code'] = EXIT_FAILURE
            self.results['exit_status'] = "Vertices must be > 2"
            return False

        return True

    def run_met_aromatic(self) -> bool:
        self.results = self.get_met_aromatic_interactions(self.code)

        if self.results['exit_code'] == EXIT_FAILURE:
            return False

        return True

    def get_joined_pairs(self) -> bool:
        for result in self.results['results']:

            pair = (
                '{}{}'.format(result['aromatic_residue'], result['aromatic_position']),
                'MET{}'.format(result['methionine_position'])
            )
            self.joined_pairs.add(pair)

    def compute_connected_components(self) -> bool:
        graph = Graph()
        graph.add_edges_from(self.joined_pairs)
        self.bridges = list(connected_components(graph))

        if not self.bridges:
            return False
        return True

    def get_bridges(self) -> bool:

        for bridge in self.bridges:
            if len(bridge) == self.vertices:
                self.results['results'].append(bridge)

        # Note that inverse bridges (MET-ARO-MET) not removed!

        if not self.results['bridges']:
            return False

        return True

    def get_bridging_interactions(self, code: str, vertices: int) -> dict:
        self.code = code
        self.vertices = vertices

        if not self.check_minimum_vertices():
            return self.results

        if not self.run_met_aromatic():
            return self.results

        self.get_joined_pairs()

        if not self.compute_connected_components():
            return self.results

        if not self.get_bridges():
            return self.results

        return self.results
