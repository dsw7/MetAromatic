from os import path
from pytest import (
    mark,
    skip,
    fail
)
from primitives.consts import EXIT_FAILURE
from data.control_data import (
    TEST_PDB_CODES,
    VALID_RESULTS_1RCY
)
from .pair import MetAromatic

TEST_PARAMETERS = {
    'distance': 4.9,
    'angle': 109.5,
    'chain': 'A',
    'model': 'cp',
}

class TestMetAromatic:

    def setup_class(self):
        self.default_parameters = {
            'cutoff_distance': 4.9,
            'cutoff_angle': 109.5,
            'chain': 'A',
            'model': 'cp',
        }

        root = path.dirname(path.dirname(path.abspath(__file__)))
        path_to_file = path.join(root, 'data/test_483OutputA3-3-M-Benchmark.csv')

        if not path.exists(path_to_file):
            fail('Path {} does not exist'.format(path_to_file))

        self.control_data = []
        for line in open(path_to_file):
            self.control_data.append(line.strip('\n').split(','))

    @mark.parametrize(
        "code",
        TEST_PDB_CODES
    )
    def test_metaromatic_algorithm_against_483_data(self, code):
        control = []
        for row in self.control_data:
            if row[7] == code:
                control.append(row)

        try:
            test_data = MetAromatic(
                **self.default_parameters
            ).get_met_aromatic_interactions(code=code)['results']

        except IndexError:
            skip('Skipping list index out of range error. Occurs because of missing data.')

        sum_norms_control = sum([float(i[6]) for i in control])
        sum_theta_control = sum([float(i[5]) for i in control])
        sum_phi_control = sum([float(i[4]) for i in control])
        sum_norms_test = sum([float(i['norm']) for i in test_data])
        sum_theta_test = sum([float(i['met_theta_angle']) for i in test_data])
        sum_phi_test = sum([float(i['met_phi_angle']) for i in test_data])

        assert abs(sum_norms_control - sum_norms_test) < 0.01
        assert abs(sum_theta_control - sum_theta_test) < 0.01
        assert abs(sum_phi_control - sum_phi_test) < 0.01


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
def test_mongodb_output_invalid_results(code: str, cutoff_distance: float, cutoff_angle: float, error: int) -> None:
    assert MetAromatic(
        cutoff_angle=cutoff_angle,
        cutoff_distance=cutoff_distance,
        chain=TEST_PARAMETERS['chain'],
        model=TEST_PARAMETERS['model']
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
def test_mongodb_output_invalid_results_exception_boolean(code: str, cutoff_distance: float, cutoff_angle: float) -> None:
    assert MetAromatic(
        cutoff_angle=cutoff_angle,
        cutoff_distance=cutoff_distance,
        chain=TEST_PARAMETERS['chain'],
        model=TEST_PARAMETERS['model']
    ).get_met_aromatic_interactions(code=code).get('exit_status')

def test_mongodb_output_valid_results() -> None:
    sum_met_theta_control = sum([i['met_theta_angle'] for i in VALID_RESULTS_1RCY])
    sum_met_phi_control = sum([i['met_phi_angle'] for i in VALID_RESULTS_1RCY])

    test_results = MetAromatic(
        **TEST_PARAMETERS
    ).get_met_aromatic_interactions(code='1rcy')['results']

    sum_met_theta_test = sum([i['met_theta_angle'] for i in test_results])
    sum_met_phi_test = sum([i['met_phi_angle'] for i in test_results])

    assert sum_met_theta_control == sum_met_theta_test
    assert sum_met_phi_control == sum_met_phi_test

def test_invalid_distance_error() -> None:
    assert MetAromatic(
        cutoff_angle=TEST_PARAMETERS['angle'],
        cutoff_distance=0.00,
        model=TEST_PARAMETERS['model'],
        chain=TEST_PARAMETERS['chain']
    ).get_met_aromatic_interactions(code='1rcy')['exit_code'] == EXIT_FAILURE

def test_invalid_angle_error() -> None:
    assert MetAromatic(
        cutoff_angle=-720.00,
        cutoff_distance=TEST_PARAMETERS['distance'],
        model=TEST_PARAMETERS['model'],
        chain=TEST_PARAMETERS['chain']
    ).get_met_aromatic_interactions(code='1rcy')['exit_code'] == EXIT_FAILURE

def test_invalid_pdb_code_error() -> None:
    assert MetAromatic(
        cutoff_angle=TEST_PARAMETERS['angle'],
        cutoff_distance=TEST_PARAMETERS['distance'],
        model=TEST_PARAMETERS['model'],
        chain=TEST_PARAMETERS['chain']
    ).get_met_aromatic_interactions(code='foo')['exit_code'] == EXIT_FAILURE

def test_no_met_coordinates_error() -> None:
    assert MetAromatic(
        cutoff_angle=TEST_PARAMETERS['angle'],
        cutoff_distance=TEST_PARAMETERS['distance'],
        model=TEST_PARAMETERS['model'],
        chain=TEST_PARAMETERS['chain']
    ).get_met_aromatic_interactions(code='3nir')['exit_code'] == EXIT_FAILURE

def test_invalid_model_error() -> None:
    assert MetAromatic(
        cutoff_angle=TEST_PARAMETERS['angle'],
        cutoff_distance=TEST_PARAMETERS['distance'],
        model='foobarbaz',
        chain=TEST_PARAMETERS['chain']
    ).get_met_aromatic_interactions(code='1rcy')['exit_code'] == EXIT_FAILURE

def test_no_results_error() -> None:
    assert MetAromatic(
        cutoff_angle=TEST_PARAMETERS['angle'],
        cutoff_distance=TEST_PARAMETERS['distance'],
        model=TEST_PARAMETERS['model'],
        chain=TEST_PARAMETERS['chain']
    ).get_met_aromatic_interactions(code='1a5r')['exit_code'] == EXIT_FAILURE
