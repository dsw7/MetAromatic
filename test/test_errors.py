from sys import path; path.append('../src')
from met_aromatic import MetAromatic
from utilities import errors


CUTOFF_483_TESTS = 4.9
ANGLE_483_TESTS = 109.5
MODEL = 'cp'
CHAIN = 'A'


def test_invalid_distance_error():
    assert MetAromatic(
        code='foobarbaz',
        cutoff_angle=ANGLE_483_TESTS,
        cutoff_distance=0.00,
        model=MODEL,
        chain=CHAIN
    ).get_met_aromatic_interactions() == errors.InvalidCutoffsError


def test_invalid_angle_error():
    assert MetAromatic(
        code='foobarbaz',
        cutoff_angle=-720.00,
        cutoff_distance=CUTOFF_483_TESTS,
        model=MODEL,
        chain=CHAIN
    ).get_met_aromatic_interactions() == errors.InvalidCutoffsError


def test_invalid_pdb_code_error():
    assert MetAromatic(
        code='foobarbaz',
        cutoff_angle=ANGLE_483_TESTS,
        cutoff_distance=CUTOFF_483_TESTS,
        model=MODEL,
        chain=CHAIN
    ).get_met_aromatic_interactions() == errors.InvalidPDBFileError


def test_no_met_coordinates_error():
    assert MetAromatic(
        code='3nir',
        cutoff_angle=ANGLE_483_TESTS,
        cutoff_distance=CUTOFF_483_TESTS,
        model=MODEL,
        chain=CHAIN
    ).get_met_aromatic_interactions() == errors.NoMetCoordinatesError


def test_invalid_model_error():
    assert MetAromatic(
        code='1rcy',
        cutoff_angle=ANGLE_483_TESTS,
        cutoff_distance=CUTOFF_483_TESTS,
        model='foobarbaz',
        chain=CHAIN
    ).get_met_aromatic_interactions() == errors.InvalidModelError


def test_no_results_error():
    assert MetAromatic(
        code='1a5r',
        cutoff_angle=ANGLE_483_TESTS,
        cutoff_distance=CUTOFF_483_TESTS,
        model=MODEL,
        chain=CHAIN
    ).get_met_aromatic_interactions() == errors.NoResultsError
