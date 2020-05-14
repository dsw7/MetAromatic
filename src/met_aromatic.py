from networkx import Graph, connected_components
from utilities import (
    filegetter,
    preprocessing,
    get_aromatic_midpoints,
    get_lone_pairs,
    distance_angular,
    errors,
    verifications
)


class MetAromatic:
    def __init__(self, code, cutoff_distance, cutoff_angle, chain, model):
        self.code = code
        self.cutoff_distance = cutoff_distance
        self.cutoff_angle = cutoff_angle
        self.chain = chain
        self.model = model

    def get_met_aromatic_interactions(self):
        results = {
            '_id': self.code,
            'exit_code': 0,
            'exit_status': None,
            'results': None
        }

        if not verifications.verify_input_distance(self.cutoff_distance):
            results['exit_status'] = "Invalid cutoff distance"
            results['exit_code'] = errors.ErrorCodes.InvalidCutoffsError
            return results

        if not verifications.verify_input_angle(self.cutoff_angle):
            results['exit_status'] = "Invalid cutoff angle"
            results['exit_code'] = errors.ErrorCodes.InvalidCutoffsError
            return results

        file_from_pdb = filegetter.PDBFileGetter(self.code)

        filepath = file_from_pdb.fetch_entry_from_pdb()
        if not filepath:
            results['exit_status'] = "Invalid PDB file"
            results['exit_code'] = errors.ErrorCodes.InvalidPDBFileError
            return results

        raw_data = preprocessing.get_raw_data_from_file(filepath)

        if not file_from_pdb.remove_entry():
            results['exit_status'] = "Could not remove PDB file"
            results['exit_code'] = errors.ErrorCodes.MissingFileError
            return results

        first_model = preprocessing.get_first_model_from_raw_data(raw_data)

        met_coordinates = preprocessing.get_relevant_met_coordinates(first_model, self.chain)

        if not met_coordinates:
            results['exit_status'] = "No MET residues"
            results['exit_code'] = errors.ErrorCodes.NoMetCoordinatesError
            return results

        phe_coordinates = preprocessing.get_relevant_phe_coordinates(first_model, self.chain)
        tyr_coordinates = preprocessing.get_relevant_tyr_coordinates(first_model, self.chain)
        trp_coordinates = preprocessing.get_relevant_trp_coordinates(first_model, self.chain)
        if not any((phe_coordinates, tyr_coordinates, trp_coordinates)):
            results['exit_status'] = "No PHE/TYR/TRP residues"
            results['exit_code'] = errors.ErrorCodes.NoAromaticCoordinatesError
            return results

        met_lone_pairs = get_lone_pairs.get_lone_pairs(met_coordinates, self.model)
        if not met_lone_pairs:
            results['exit_status'] = "Invalid model"
            results['exit_code'] = errors.ErrorCodes.InvalidModelError
            return results

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
            results['exit_status'] = "No interactions"
            results['exit_code'] = errors.ErrorCodes.NoResultsError
            return results

        results['results'] = interactions

        return results

    def get_bridging_interactions(self, number_vertices=3):
        if number_vertices < 3:
            return errors.ErrorCodes.BadVerticesError

        met_aromatic_results = self.get_met_aromatic_interactions()

        if isinstance(met_aromatic_results, list):
            joined_pairs = list(set(
                (''.join(pair[0:2]), ''.join(pair[2:4])) for pair in met_aromatic_results
            ))

            nx_graph = Graph()
            nx_graph.add_edges_from(joined_pairs)

            bridges = list(connected_components(nx_graph))
            return [
                bridge for bridge in bridges if len(bridge) == number_vertices
            ]  # note that inverse bridges (MET-ARO-MET) not removed!

        else:
            return met_aromatic_results


    def get_met_aromatic_interactions_mongodb_output(self, round_to_number=3):
        met_aromatic_results = self.get_met_aromatic_interactions()

        if isinstance(met_aromatic_results, list):
            results = []
            for row in met_aromatic_results:
                results.append({
                    'aromatic_residue': row[0],
                    'aromatic_position': int(row[1]),
                    'methionine_position': int(row[3]),
                    'norm': round(row[4], round_to_number),
                    'met_theta_angle': round(row[5], round_to_number),
                    'met_phi_angle': round(row[6], round_to_number)
                })

            return {
                '_id': self.code,
                'exception': False,
                'results': results
            }

        else:
            return {
                '_id': self.code,
                'exception': True,
                'error_code': met_aromatic_results
            }
