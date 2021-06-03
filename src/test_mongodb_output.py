from pytest import mark
from .met_aromatic import MetAromatic
from .primitives.consts import EXIT_FAILURE

VALID_RESULTS_1RCY = [{
    'aromatic_residue': 'TYR',
    'aromatic_position': '122',
    'methionine_position': '18',
    'norm': 4.211,
    'met_theta_angle': 75.766,
    'met_phi_angle': 64.317
}, {
    'aromatic_residue': 'TYR',
    'aromatic_position': '122',
    'methionine_position': '18',
    'norm': 3.954,
    'met_theta_angle': 60.145,
    'met_phi_angle': 68.352
}, {
    'aromatic_residue': 'TYR',
    'aromatic_position': '122',
    'methionine_position': '18',
    'norm': 4.051,
    'met_theta_angle': 47.198,
    'met_phi_angle': 85.151
}, {
    'aromatic_residue': 'TYR',
    'aromatic_position': '122',
    'methionine_position': '18',
    'norm': 4.39,
    'met_theta_angle': 53.4,
    'met_phi_angle': 95.487
}, {
    'aromatic_residue': 'TYR',
    'aromatic_position': '122',
    'methionine_position': '18',
    'norm': 4.62,
    'met_theta_angle': 68.452,
    'met_phi_angle': 90.771
}, {
    'aromatic_residue': 'TYR',
    'aromatic_position': '122',
    'methionine_position': '18',
    'norm': 4.537,
    'met_theta_angle': 78.568,
    'met_phi_angle': 76.406
}, {
    'aromatic_residue': 'PHE',
    'aromatic_position': '54',
    'methionine_position': '148',
    'norm': 4.777,
    'met_theta_angle': 105.947,
    'met_phi_angle': 143.022
}, {
    'aromatic_residue': 'PHE',
    'aromatic_position': '54',
    'methionine_position': '148',
    'norm': 4.61,
    'met_theta_angle': 93.382,
    'met_phi_angle': 156.922
}, {
    'aromatic_residue': 'PHE',
    'aromatic_position': '54',
    'methionine_position': '148',
    'norm': 4.756,
    'met_theta_angle': 93.287,
    'met_phi_angle': 154.63
}]


class TestMongoDBOutput:
    def setup_class(self):
        self.default_parameters = {
            'cutoff_distance': 4.9,
            'cutoff_angle': 109.5,
            'chain': 'A',
            'model': 'cp',
        }

    @mark.parametrize(
        'code, cutoff_distance, cutoff_angle, error',
        [
            ('1rcy', 0.00, 109.5, EXIT_FAILURE),
            ('1rcy', 4.95, 720.0, EXIT_FAILURE),
            ('2rcy', 4.95, 109.5, EXIT_FAILURE),
            ('3nir', 4.95, 109.5, EXIT_FAILURE),
            ('abcd', 4.95, 109.5, EXIT_FAILURE)
        ],
        ids=[
            "Testing InvalidCutoffsError - 1",
            "Testing InvalidCutoffsError - 2",
            "Testing NoMetCoordinatesError - 1",
            "Testing NoMetCoordinatesError - 2",
            "Testing InvalidPDBFileError"
        ]
    )
    def test_mongodb_output_invalid_results(self, code, cutoff_distance, cutoff_angle, error):
        assert MetAromatic(
            cutoff_angle=cutoff_angle,
            cutoff_distance=cutoff_distance,
            chain=self.default_parameters['chain'],
            model=self.default_parameters['model']
        ).get_met_aromatic_interactions(code=code)['exit_code'] == error

    @mark.parametrize(
        'code, cutoff_distance, cutoff_angle',
        [
            ('1rcy', 0.00, 109.5),
            ('1rcy', 4.95, 720.0),
            ('2rcy', 4.95, 109.5),
            ('3nir', 4.95, 109.5),
            ('abcd', 4.95, 109.5)
        ]
    )
    def test_mongodb_output_invalid_results_exception_boolean(self, code, cutoff_distance, cutoff_angle):
        assert MetAromatic(
            cutoff_angle=cutoff_angle,
            cutoff_distance=cutoff_distance,
            chain=self.default_parameters['chain'],
            model=self.default_parameters['model']
        ).get_met_aromatic_interactions(code=code).get('exit_status')

    def test_mongodb_output_valid_results(self):
        sum_met_theta_control = sum([i['met_theta_angle'] for i in VALID_RESULTS_1RCY])
        sum_met_phi_control = sum([i['met_phi_angle'] for i in VALID_RESULTS_1RCY])

        test_results = MetAromatic(
            **self.default_parameters
        ).get_met_aromatic_interactions(code='1rcy')['results']

        sum_met_theta_test = sum([i['met_theta_angle'] for i in test_results])
        sum_met_phi_test = sum([i['met_phi_angle'] for i in test_results])

        assert sum_met_theta_control == sum_met_theta_test
        assert sum_met_phi_control == sum_met_phi_test
