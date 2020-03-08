from networkx import Graph, connected_components
from .utilities import filegetter
from .utilities import preprocessing
from .utilities import get_aromatic_midpoints
from .utilities import get_lone_pairs
from .utilities import distance_angular
from .utilities import errors
from .utilities import verifications


class MetAromatic:
    def __init__(self, code, cutoff_distance, cutoff_angle, chain, model):
        self.code = code
        self.cutoff_distance = cutoff_distance
        self.cutoff_angle = cutoff_angle
        self.chain = chain
        self.model = model

    def get_met_aromatic_interactions(self):
        if not verifications.verify_input_distance(self.cutoff_distance) \
        or not verifications.verify_input_angle(self.cutoff_angle):
            return errors.InvalidCutoffsError

        file_from_pdb = filegetter.PDBFileGetter(self.code)

        filepath = file_from_pdb.fetch_entry_from_pdb()
        if not filepath:
            return errors.InvalidPDBFileError

        raw_data = preprocessing.get_raw_data_from_file(filepath)

        if not file_from_pdb.remove_entry():
            return errors.MissingFileError

        first_model = preprocessing.get_first_model_from_raw_data(raw_data)

        met_coordinates = preprocessing.get_relevant_met_coordinates(first_model, self.chain)

        if not met_coordinates:
            return errors.NoMetCoordinatesError

        phe_coordinates = preprocessing.get_relevant_phe_coordinates(first_model, self.chain)
        tyr_coordinates = preprocessing.get_relevant_tyr_coordinates(first_model, self.chain)
        trp_coordinates = preprocessing.get_relevant_trp_coordinates(first_model, self.chain)
        if not any((phe_coordinates, tyr_coordinates, trp_coordinates)):
            return errors.NoAromaticCoordinatesError

        met_lone_pairs = get_lone_pairs.get_lone_pairs(met_coordinates, self.model)
        if not met_lone_pairs:
            return errors.InvalidModelError

        phe_midpoints = get_aromatic_midpoints.get_phe_midpoints(phe_coordinates)
        tyr_midpoints = get_aromatic_midpoints.get_tyr_midpoints(tyr_coordinates)
        trp_midpoints = get_aromatic_midpoints.get_trp_midpoints(trp_coordinates)

        interactions = distance_angular.apply_distance_angular_condition(
            phe_midpoints + tyr_midpoints + trp_midpoints,
            met_lone_pairs,
            self.cutoff_distance,
            self.cutoff_angle
        )

        if not interactions:
            return errors.NoResultsError

        return interactions


    def get_bridging_interactions(self, number_vertices=3):
        if number_vertices < 3:
            return errors.BadVerticesError

        aromatic_interactions = self.get_met_aromatic_interactions()
        if not (isinstance(aromatic_interactions, list)) and \
               (issubclass(aromatic_interactions, errors.Error)):
            return aromatic_interactions

        joined_pairs = list(set(
            (''.join(pair[0:2]), ''.join(pair[2:4])) for pair in aromatic_interactions
        ))

        nx_graph = Graph()
        nx_graph.add_edges_from(joined_pairs)

        bridges = list(connected_components(nx_graph))
        return [
            bridge for bridge in bridges if len(bridge) == number_vertices
        ]  # note that inverse bridges (MET-ARO-MET) not removed!


    def get_met_aromatic_interactions_mongodb_output(self, round_to_number=3):
        aromatic_interactions = self.get_met_aromatic_interactions()
        if not (isinstance(aromatic_interactions, list)) and \
               (issubclass(aromatic_interactions, errors.Error)):
            return aromatic_interactions

        results = []
        for row in aromatic_interactions:
            results.append({
                'aromatic_residue': row[0],
                'aromatic_position': row[1],
                'methionine_position': row[3],
                'norm': round(row[4], round_to_number),
                'met_theta_angle': round(row[5], round_to_number),
                'met_phi_angle': round(row[6], round_to_number)
            })

        return {
            '_id': self.code,
            'results': results
        }
