from subprocess import run, DEVNULL
from pytest import mark
from utilities import errors


EXIT_SUCCESS = 0
EXIT_GENERAL_PROGRAM_FAILURES = 2


def test_aromatic_interaction_working_query(path_runner):
    assert run(
        f'python {path_runner} --ai --code 1rcy',
        stdout=DEVNULL,
        check=True
    ).returncode == EXIT_SUCCESS


def test_bridging_interaction_working_query(path_runner):
    assert run(
        f'python {path_runner} --bi --code 1rcy',
        stdout=DEVNULL,
        check=True
    ).returncode == EXIT_SUCCESS


def test_bridging_interaction_working_query_vertices_3(path_runner):
    assert run(
        f'python {path_runner} --bi --code 1rcy --vertices 3',
        stdout=DEVNULL,
        check=True
    ).returncode == EXIT_SUCCESS


def test_bridging_interaction_working_query_vertices_2(path_runner):
    assert run(
        f'python {path_runner} --bi --code 1rcy --vertices 2',
        stdout=DEVNULL,
        check=True
    ).returncode == errors.ErrorCodes.BadVerticesError


def test_invalid_cutoff_distance(path_runner):
    assert run(
        f'python {path_runner} --ai --code 1rcy --cutoff_distance 0.00',
        check=True
    ).returncode == errors.ErrorCodes.InvalidCutoffsError


def test_invalid_cutoff_distance_stringified(path_runner):
    assert run(
        f'python {path_runner} --ai --code 1rcy --cutoff_distance foo',
        stderr=DEVNULL,
        check=True
    ).returncode == EXIT_GENERAL_PROGRAM_FAILURES


def test_invalid_cutoff_angle(path_runner):
    assert run(
        f'python {path_runner} --ai --code 1rcy --cutoff_angle 361.00',
        check=True
    ).returncode == errors.ErrorCodes.InvalidCutoffsError


def test_invalid_code(path_runner):
    assert run(
        f'python {path_runner} --ai --code foobar',
        check=True
    ).returncode == errors.ErrorCodes.InvalidPDBFileError


def test_no_met_coordinates(path_runner):
    assert run(
        f'python {path_runner} --ai --code 3nir',
        check=True
    ).returncode == errors.ErrorCodes.NoMetCoordinatesError


def test_invalid_model(path_runner):
    assert run(
        f'python {path_runner} --ai --code 1rcy --model foobarbaz',
        check=True
    ).returncode == errors.ErrorCodes.InvalidModelError


def test_no_results(path_runner):
    assert run(
        f'python {path_runner} --ai --code 1a5r',
        check=True
    ).returncode == errors.ErrorCodes.NoResultsError


def test_bad_query_type(path_runner):
    assert run(
        f'python {path_runner} --ai --code 1rcy --query foobarbaz',
        stderr=DEVNULL,
        check=True
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
        stderr=DEVNULL,
        check=True
    ).returncode == EXIT_GENERAL_PROGRAM_FAILURES
