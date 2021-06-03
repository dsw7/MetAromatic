from .met_aromatic import MetAromatic
from .primitives.consts import EXIT_FAILURE


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
            cutoff_angle=self.default_parameters['angle'],
            cutoff_distance=0.00,
            model=self.default_parameters['model'],
            chain=self.default_parameters['chain']
        ).get_met_aromatic_interactions(code='1rcy')['exit_code'] == EXIT_FAILURE

    def test_invalid_angle_error(self):
        assert MetAromatic(
            cutoff_angle=-720.00,
            cutoff_distance=self.default_parameters['distance'],
            model=self.default_parameters['model'],
            chain=self.default_parameters['chain']
        ).get_met_aromatic_interactions(code='1rcy')['exit_code'] == EXIT_FAILURE

    def test_invalid_pdb_code_error(self):
        assert MetAromatic(
            cutoff_angle=self.default_parameters['angle'],
            cutoff_distance=self.default_parameters['distance'],
            model=self.default_parameters['model'],
            chain=self.default_parameters['chain']
        ).get_met_aromatic_interactions(code='foo')['exit_code'] == EXIT_FAILURE

    def test_no_met_coordinates_error(self):
        assert MetAromatic(
            cutoff_angle=self.default_parameters['angle'],
            cutoff_distance=self.default_parameters['distance'],
            model=self.default_parameters['model'],
            chain=self.default_parameters['chain']
        ).get_met_aromatic_interactions(code='3nir')['exit_code'] == EXIT_FAILURE

    def test_invalid_model_error(self):
        assert MetAromatic(
            cutoff_angle=self.default_parameters['angle'],
            cutoff_distance=self.default_parameters['distance'],
            model='foobarbaz',
            chain=self.default_parameters['chain']
        ).get_met_aromatic_interactions(code='1rcy')['exit_code'] == EXIT_FAILURE

    def test_no_results_error(self):
        assert MetAromatic(
            cutoff_angle=self.default_parameters['angle'],
            cutoff_distance=self.default_parameters['distance'],
            model=self.default_parameters['model'],
            chain=self.default_parameters['chain']
        ).get_met_aromatic_interactions(code='1a5r')['exit_code'] == EXIT_FAILURE
