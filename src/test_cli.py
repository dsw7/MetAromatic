from subprocess import call, DEVNULL
from pytest import mark
from utilities import errors


EXIT_SUCCESS = 0
EXIT_GENERAL_PROGRAM_FAILURES = 2


def test_aromatic_interaction_working_query(path_runner):
    assert call(
        f'python {path_runner} --ai --code 1rcy'.split(),
        stdout=DEVNULL
    ) == EXIT_SUCCESS


def test_bridging_interaction_working_query(path_runner):
    assert call(
        f'python {path_runner} --bi --code 1rcy'.split(),
        stdout=DEVNULL
    ) == EXIT_SUCCESS


def test_bridging_interaction_working_query_vertices_3(path_runner):
    assert call(
        f'python {path_runner} --bi --code 1rcy --vertices 3'.split(),
        stdout=DEVNULL
    ) == EXIT_SUCCESS


def test_bridging_interaction_working_query_vertices_2(path_runner):
    assert call(
        f'python {path_runner} --bi --code 1rcy --vertices 2'.split(),
        stdout=DEVNULL
    ) == errors.ErrorCodes.BadVerticesError


def test_invalid_cutoff_distance(path_runner):
    assert call(
        f'python {path_runner} --ai --code 1rcy --cutoff_distance 0.00'.split()
    ) == errors.ErrorCodes.InvalidCutoffsError


def test_invalid_cutoff_distance_stringified(path_runner):
    assert call(
        f'python {path_runner} --ai --code 1rcy --cutoff_distance foo'.split(),
        stderr=DEVNULL
    ) == EXIT_GENERAL_PROGRAM_FAILURES


def test_invalid_cutoff_angle(path_runner):
    assert call(
        f'python {path_runner} --ai --code 1rcy --cutoff_angle 361.00'.split()
    ) == errors.ErrorCodes.InvalidCutoffsError


def test_invalid_code(path_runner):
    assert call(
        f'python {path_runner} --ai --code foobar'.split()
    ) == errors.ErrorCodes.InvalidPDBFileError


def test_no_met_coordinates(path_runner):
    assert call(
        f'python {path_runner} --ai --code 3nir'.split()
    ) == errors.ErrorCodes.NoMetCoordinatesError


def test_invalid_model(path_runner):
    assert call(
        f'python {path_runner} --ai --code 1rcy --model foobarbaz'.split()
    ) == errors.ErrorCodes.InvalidModelError


def test_no_results(path_runner):
    assert call(
        f'python {path_runner} --ai --code 1a5r'.split()
    ) == errors.ErrorCodes.NoResultsError


def test_bad_query_type(path_runner):
    assert call(
        f'python {path_runner} --ai --code 1rcy --query foobarbaz'.split(),
        stderr=DEVNULL
    ) == EXIT_GENERAL_PROGRAM_FAILURES


@mark.parametrize(
    'subquery',
    [
        '--ai --code ',
        '--ai --code 1rcy --cutoff_distance foobar',
        '--ai --code 1rcy --cutoff_angle foobar',
        '--ai --code 1rcy --vertices foo'
    ]
)
def test_general_argparse_failures(subquery, path_runner):
    assert call(
        f'python {path_runner} {subquery}'.split(),
        stderr=DEVNULL
    ) == EXIT_GENERAL_PROGRAM_FAILURES
