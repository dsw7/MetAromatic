from subprocess import run, DEVNULL
from pytest import mark
from .utilities import errors


EXIT_SUCCESS = 0
EXIT_GENERAL_PROGRAM_FAILURES = 2


def test_aromatic_interaction_working_query(path_runner):
    assert run(
        f'python {path_runner} --ai --code 1rcy',
        stdout=DEVNULL
    ).returncode == EXIT_SUCCESS


def test_bridging_interaction_working_query(path_runner):
    assert run(
        f'python {path_runner} --bi --code 1rcy',
        stdout=DEVNULL
    ).returncode == EXIT_SUCCESS


def test_bridging_interaction_working_query_vertices_3(path_runner):
    assert run(
        f'python {path_runner} --bi --code 1rcy --vertices 3',
        stdout=DEVNULL
    ).returncode == EXIT_SUCCESS


def test_bridging_interaction_working_query_vertices_2(path_runner):
    assert run(
        f'python {path_runner} --bi --code 1rcy --vertices 2',
        stdout=DEVNULL
    ).returncode == errors.ErrorCodes.BadVerticesError


def test_invalid_cutoff_distance(path_runner):
    assert run(
        f'python {path_runner} --ai --code 1rcy --cutoff_distance 0.00'
    ).returncode == errors.ErrorCodes.InvalidCutoffs


def test_invalid_cutoff_distance_stringified(path_runner):
    assert run(
        f'python {path_runner} --ai --code 1rcy --cutoff_distance foo',
        stderr=DEVNULL
    ).returncode == EXIT_GENERAL_PROGRAM_FAILURES


def test_invalid_cutoff_angle(path_runner):
    assert run(
        f'python {path_runner} --ai --code 1rcy --cutoff_angle 361.00'
    ).returncode == errors.ErrorCodes.InvalidCutoffs


def test_invalid_code(path_runner):
    assert run(
        f'python {path_runner} --ai --code foobar'
    ).returncode == errors.ErrorCodes.InvalidPDBFile


def test_no_met_coordinates(path_runner):
    assert run(
        f'python {path_runner} --ai --code 3nir'
    ).returncode == errors.ErrorCodes.NoMetCoordinates


def test_invalid_model(path_runner):
    assert run(
        f'python {path_runner} --ai --code 1rcy --model foobarbaz'
    ).returncode == errors.ErrorCodes.InvalidModel


def test_no_results(path_runner):
    assert run(
        f'python {path_runner} --ai --code 1a5r'
    ).returncode == errors.ErrorCodes.NoResults


def test_bad_query_type(path_runner):
    assert run(
        f'python {path_runner} --ai --code 1rcy --query foobarbaz',
        stderr=DEVNULL
    ).returncode == EXIT_GENERAL_PROGRAM_FAILURES


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
    assert run(
        f'python {path_runner} {subquery}',
        stderr=DEVNULL
    ).returncode == EXIT_GENERAL_PROGRAM_FAILURES
