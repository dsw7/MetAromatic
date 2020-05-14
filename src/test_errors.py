from met_aromatic import MetAromatic
from utilities import errors


def test_invalid_distance_error(default_met_aromatic_parameters):
    assert MetAromatic(
        code='foobarbaz',
        cutoff_angle=default_met_aromatic_parameters['angle'],
        cutoff_distance=0.00,
        model=default_met_aromatic_parameters['model'],
        chain=default_met_aromatic_parameters['chain']
    ).get_met_aromatic_interactions()['exit_code'] == errors.ErrorCodes.InvalidCutoffsError


def test_invalid_angle_error(default_met_aromatic_parameters):
    assert MetAromatic(
        code='foobarbaz',
        cutoff_angle=-720.00,
        cutoff_distance=default_met_aromatic_parameters['distance'],
        model=default_met_aromatic_parameters['model'],
        chain=default_met_aromatic_parameters['chain']
    ).get_met_aromatic_interactions()['exit_code'] == errors.ErrorCodes.InvalidCutoffsError


def test_invalid_pdb_code_error(default_met_aromatic_parameters):
    assert MetAromatic(
        code='foobarbaz',
        cutoff_angle=default_met_aromatic_parameters['angle'],
        cutoff_distance=default_met_aromatic_parameters['distance'],
        model=default_met_aromatic_parameters['model'],
        chain=default_met_aromatic_parameters['chain']
    ).get_met_aromatic_interactions()['exit_code'] == errors.ErrorCodes.InvalidPDBFileError


def test_no_met_coordinates_error(default_met_aromatic_parameters):
    assert MetAromatic(
        code='3nir',
        cutoff_angle=default_met_aromatic_parameters['angle'],
        cutoff_distance=default_met_aromatic_parameters['distance'],
        model=default_met_aromatic_parameters['model'],
        chain=default_met_aromatic_parameters['chain']
    ).get_met_aromatic_interactions()['exit_code'] == errors.ErrorCodes.NoMetCoordinatesError


def test_invalid_model_error(default_met_aromatic_parameters):
    assert MetAromatic(
        code='1rcy',
        cutoff_angle=default_met_aromatic_parameters['angle'],
        cutoff_distance=default_met_aromatic_parameters['distance'],
        model='foobarbaz',
        chain=default_met_aromatic_parameters['chain']
    ).get_met_aromatic_interactions()['exit_code'] == errors.ErrorCodes.InvalidModelError


def test_no_results_error(default_met_aromatic_parameters):
    assert MetAromatic(
        code='1a5r',
        cutoff_angle=default_met_aromatic_parameters['angle'],
        cutoff_distance=default_met_aromatic_parameters['distance'],
        model=default_met_aromatic_parameters['model'],
        chain=default_met_aromatic_parameters['chain']
    ).get_met_aromatic_interactions()['exit_code'] == errors.ErrorCodes.NoResultsError
