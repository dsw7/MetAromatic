from subprocess import run, DEVNULL
from pytest import mark
from .utilities import errors


EXIT_SUCCESS = 0
EXIT_GENERAL_PROGRAM_FAILURES = 2


def test_working_query(path_runner):
    assert run(
        f'python {path_runner} --code 1rcy',
        stdout=DEVNULL
    ).returncode == EXIT_SUCCESS


def test_invalid_cutoff_distance(path_runner):
    assert run(
        f'python {path_runner} --code 1rcy --cutoff_distance 0.00'
    ).returncode == errors.ErrorCodes.InvalidCutoffs


def test_invalid_cutoff_angle(path_runner):
    assert run(
        f'python {path_runner} --code 1rcy --cutoff_angle 361.00'
    ).returncode == errors.ErrorCodes.InvalidCutoffs


def test_invalid_code(path_runner):
    assert run(
        f'python {path_runner} --code foobar'
    ).returncode == errors.ErrorCodes.InvalidPDBFile


def test_no_met_coordinates(path_runner):
    assert run(
        f'python {path_runner} --code 3nir'
    ).returncode == errors.ErrorCodes.NoMetCoordinates


def test_invalid_model(path_runner):
    assert run(
        f'python {path_runner} --code 1rcy --model foobarbaz'
    ).returncode == errors.ErrorCodes.InvalidModel


def test_no_results(path_runner):
    assert run(
        f'python {path_runner} --code 1a5r'
    ).returncode == errors.ErrorCodes.NoResults


def test_bad_query_type(path_runner):
    assert run(
        f'python {path_runner} --code 1rcy --query foobarbaz'
    ).returncode == errors.ErrorCodes.BadQueryType


@mark.parametrize(
    'subquery',
    [
        '--code ',
        '--code 1rcy --cutoff_distance foobar',
        '--code 1rcy --cutoff_angle foobar',
        '--code 1rcy --vertices foo'
    ]
)
def test_general_argparse_failures(subquery, path_runner):
    assert run(
        f'python {path_runner} {subquery}',
        stderr=DEVNULL
    ).returncode == EXIT_GENERAL_PROGRAM_FAILURES
