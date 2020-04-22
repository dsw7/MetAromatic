from os import path, chdir, getcwd
from subprocess import call, DEVNULL
from pytest import mark
from utilities import errors


EXIT_SUCCESS = 0
EXIT_GENERAL_PROGRAM_FAILURES = 2


def test_aromatic_interaction_run_from_parent_directory(path_runner):
    pwd = getcwd()
    chdir(path.dirname(path.dirname(path_runner)))
    retval = call(
        f'python3 MetAromatic/runner.py --ai 1rcy'.split(),
        stdout=DEVNULL
    )
    chdir(pwd)
    assert retval == EXIT_SUCCESS


def test_aromatic_interaction_run_from_child_directory(path_runner):
    pwd = getcwd()
    chdir(path.join(path.dirname(path_runner), 'src/'))
    retval = call(
        f'python3 ../runner.py --ai 1rcy'.split(),
        stdout=DEVNULL
    )
    chdir(pwd)
    assert retval == EXIT_SUCCESS


def test_aromatic_interaction_run_from_child_child_directory(path_runner):
    pwd = getcwd()
    chdir(path.join(path.dirname(path_runner), 'src/utilities'))
    retval = call(
        f'python3 ../../runner.py --ai 1rcy'.split(),
        stdout=DEVNULL
    )
    chdir(pwd)
    assert retval == EXIT_SUCCESS


def test_bridging_interaction_run_from_parent_directory(path_runner):
    pwd = getcwd()
    chdir(path.dirname(path.dirname(path_runner)))
    retval = call(
        f'python3 MetAromatic/runner.py --bi 6lu7'.split(),
        stdout=DEVNULL
    )
    chdir(pwd)
    assert retval == EXIT_SUCCESS


def test_bridging_interaction_run_from_child_directory(path_runner):
    pwd = getcwd()
    chdir(path.join(path.dirname(path_runner), 'src/'))
    retval = call(
        f'python3 ../runner.py --bi 6lu7'.split(),
        stdout=DEVNULL
    )
    chdir(pwd)
    assert retval == EXIT_SUCCESS


def test_bridging_interaction_run_from_child_child_directory(path_runner):
    pwd = getcwd()
    chdir(path.join(path.dirname(path_runner), 'src/utilities'))
    retval = call(
        f'python3 ../../runner.py --bi 6lu7'.split(),
        stdout=DEVNULL
    )
    chdir(pwd)
    assert retval == EXIT_SUCCESS


def test_aromatic_interaction_working_query(path_runner):
    assert call(
        f'python3 {path_runner} --ai 1rcy'.split(),
        stdout=DEVNULL
    ) == EXIT_SUCCESS


def test_bridging_interaction_working_query(path_runner):
    assert call(
        f'python3 {path_runner} --bi 1rcy'.split(),
        stdout=DEVNULL
    ) == EXIT_SUCCESS


def test_bridging_interaction_working_query_vertices_3(path_runner):
    assert call(
        f'python3 {path_runner} --bi 1rcy --vertices 3'.split(),
        stdout=DEVNULL
    ) == EXIT_SUCCESS


def test_bridging_interaction_working_query_vertices_2(path_runner):
    assert call(
        f'python3 {path_runner} --bi 1rcy --vertices 2'.split(),
        stdout=DEVNULL
    ) == errors.ErrorCodes.BadVerticesError


def test_invalid_cutoff_distance(path_runner):
    assert call(
        f'python3 {path_runner} --ai 1rcy --cutoff_distance 0.00'.split()
    ) == errors.ErrorCodes.InvalidCutoffsError


def test_invalid_cutoff_distance_stringified(path_runner):
    assert call(
        f'python3 {path_runner} --ai 1rcy --cutoff_distance foo'.split(),
        stderr=DEVNULL
    ) == EXIT_GENERAL_PROGRAM_FAILURES


def test_invalid_cutoff_angle(path_runner):
    assert call(
        f'python3 {path_runner} --ai 1rcy --cutoff_angle 361.00'.split()
    ) == errors.ErrorCodes.InvalidCutoffsError


def test_invalid_code(path_runner):
    assert call(
        f'python3 {path_runner} --ai foobar'.split()
    ) == errors.ErrorCodes.InvalidPDBFileError


def test_no_met_coordinates(path_runner):
    assert call(
        f'python3 {path_runner} --ai 3nir'.split()
    ) == errors.ErrorCodes.NoMetCoordinatesError


def test_invalid_model(path_runner):
    assert call(
        f'python3 {path_runner} --ai 1rcy --model foobarbaz'.split()
    ) == errors.ErrorCodes.InvalidModelError


def test_no_results(path_runner):
    assert call(
        f'python3 {path_runner} --ai 1a5r'.split()
    ) == errors.ErrorCodes.NoResultsError


def test_bad_query_type(path_runner):
    assert call(
        f'python3 {path_runner} --ai 1rcy --query foobarbaz'.split(),
        stderr=DEVNULL
    ) == EXIT_GENERAL_PROGRAM_FAILURES


@mark.parametrize(
    'subquery',
    [
        '--ai ',
        '--ai 1rcy --bi 1rcy',
        '--ai 1rcy --cutoff_distance foobar',
        '--ai 1rcy --cutoff_angle foobar',
        '--ai 1rcy --vertices foo',
        '--batch ',
    ]
)
def test_general_argparse_failures(subquery, path_runner):
    assert call(
        f'python3 {path_runner} {subquery}'.split(),
        stderr=DEVNULL
    ) == EXIT_GENERAL_PROGRAM_FAILURES
