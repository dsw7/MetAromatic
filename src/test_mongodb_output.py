from pytest import mark
from .met_aromatic import MetAromatic
from .utilities import errors


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


@mark.parametrize(
    'code, cutoff_distance, cutoff_angle, error',
    [
        ('1rcy', 0.00, 109.5, errors.ErrorCodes.InvalidCutoffsError),
        ('1rcy', 4.95, 720.0, errors.ErrorCodes.InvalidCutoffsError),
        ('2rcy', 4.95, 109.5, errors.ErrorCodes.NoMetCoordinatesError),
        ('3nir', 4.95, 109.5, errors.ErrorCodes.NoMetCoordinatesError),
        ('abcd', 4.95, 109.5, errors.ErrorCodes.InvalidPDBFileError)
    ],
    ids=[
        "Testing errors.ErrorCodes.InvalidCutoffsError - 1",
        "Testing errors.ErrorCodes.InvalidCutoffsError - 2",
        "Testing errors.ErrorCodes.NoMetCoordinatesError - 1",
        "Testing errors.ErrorCodes.NoMetCoordinatesError - 2",
        "Testing errors.ErrorCodes.InvalidPDBFileError"
    ]
)
def test_mongodb_output_invalid_results(code, cutoff_distance, cutoff_angle, default_met_aromatic_parameters, error):
    assert MetAromatic(
        code=code,
        cutoff_angle=cutoff_angle,
        cutoff_distance=cutoff_distance,
        chain=default_met_aromatic_parameters['chain'],
        model=default_met_aromatic_parameters['model']
    ).get_met_aromatic_interactions_mongodb_output().get('error_code') == error


def test_mongodb_output_valid_results(default_met_aromatic_parameters):
    assert MetAromatic(
        code='1rcy',
        cutoff_angle=default_met_aromatic_parameters['angle'],
        cutoff_distance=default_met_aromatic_parameters['distance'],
        chain=default_met_aromatic_parameters['chain'],
        model=default_met_aromatic_parameters['model']
    ).get_met_aromatic_interactions_mongodb_output() == VALID_RESULTS_1RCY
