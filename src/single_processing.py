import sys
from met_aromatic import MetAromatic
from utilities.logger import print_error


class RunSingleQuery:
    def __init__(self, command_line_arguments):
        self.command_line_arguments = command_line_arguments
        self.header_success = ['ARO', 'POS', 'MET POS', 'NORM', 'MET-THETA', 'MET-PHI']

    def single_met_aromatic_query(self):
        results = MetAromatic(
            self.command_line_arguments.single_aromatic_interaction_query,
            cutoff_distance=self.command_line_arguments.cutoff_distance,
            cutoff_angle=self.command_line_arguments.cutoff_angle,
            chain=self.command_line_arguments.chain,
            model=self.command_line_arguments.model
        ).get_met_aromatic_interactions()

        if results['exit_code'] == 0:
            print("{:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(*self.header_success))
            for line in results['results']:
                print("{:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(*line.values()))
        else:
            print_error(results['exit_status'])
            print_error(f"Exited with code: {results['exit_code']}")

        sys.exit(results['exit_code'])

    def single_bridging_interaction_query(self):
        results = MetAromatic(
            self.command_line_arguments.single_bridging_interaction_query,
            cutoff_distance=self.command_line_arguments.cutoff_distance,
            cutoff_angle=self.command_line_arguments.cutoff_angle,
            chain=self.command_line_arguments.chain,
            model=self.command_line_arguments.model
        ).get_bridging_interactions(
            number_vertices=self.command_line_arguments.vertices
        )

        if results['exit_code'] == 0:
            print(results['results'])
        else:
            print_error(results['exit_status'])
            print_error(f"Exited with code: {results['exit_code']}")

        sys.exit(results['exit_code'])
