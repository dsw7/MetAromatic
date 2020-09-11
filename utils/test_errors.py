from met_aromatic import MetAromatic
from consts import EXIT_FAILURE


class TestErrors:
    def setup_class(self):
        self.default_parameters = {
            'distance': 4.9,
            'angle': 109.5,
            'chain': 'A',
            'model': 'cp',
        }

    def test_invalid_distance_error(self):
        assert MetAromatic(
            code='foobarbaz',
            cutoff_angle=self.default_parameters['angle'],
            cutoff_distance=0.00,
            model=self.default_parameters['model'],
            chain=self.default_parameters['chain']
        ).get_met_aromatic_interactions()['exit_code'] == EXIT_FAILURE

    def test_invalid_angle_error(self):
        assert MetAromatic(
            code='foobarbaz',
            cutoff_angle=-720.00,
            cutoff_distance=self.default_parameters['distance'],
            model=self.default_parameters['model'],
            chain=self.default_parameters['chain']
        ).get_met_aromatic_interactions()['exit_code'] == EXIT_FAILURE

    def test_invalid_pdb_code_error(self):
        assert MetAromatic(
            code='foobarbaz',
            cutoff_angle=self.default_parameters['angle'],
            cutoff_distance=self.default_parameters['distance'],
            model=self.default_parameters['model'],
            chain=self.default_parameters['chain']
        ).get_met_aromatic_interactions()['exit_code'] == EXIT_FAILURE

    def test_no_met_coordinates_error(self):
        assert MetAromatic(
            code='3nir',
            cutoff_angle=self.default_parameters['angle'],
            cutoff_distance=self.default_parameters['distance'],
            model=self.default_parameters['model'],
            chain=self.default_parameters['chain']
        ).get_met_aromatic_interactions()['exit_code'] == EXIT_FAILURE

    def test_invalid_model_error(self):
        assert MetAromatic(
            code='1rcy',
            cutoff_angle=self.default_parameters['angle'],
            cutoff_distance=self.default_parameters['distance'],
            model='foobarbaz',
            chain=self.default_parameters['chain']
        ).get_met_aromatic_interactions()['exit_code'] == EXIT_FAILURE

    def test_no_results_error(self):
        assert MetAromatic(
            code='1a5r',
            cutoff_angle=self.default_parameters['angle'],
            cutoff_distance=self.default_parameters['distance'],
            model=self.default_parameters['model'],
            chain=self.default_parameters['chain']
        ).get_met_aromatic_interactions()['exit_code'] == EXIT_FAILURE
