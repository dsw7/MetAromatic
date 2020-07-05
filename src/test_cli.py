from os import path, chdir, getcwd
from platform import system
from subprocess import call, DEVNULL
from pytest import mark
from utilities import errors

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_GENERAL_PROGRAM_FAILURES = 2

if 'Windows' in system():
    INTERP = 'python'
else:
    INTERP = 'python3'


class TestCommandLineInterface:
    def setup_class(self):
        root = path.dirname(path.dirname(path.abspath(__file__)))
        self.path_runner = path.join(root, 'runner.py')

    def test_aromatic_interaction_working_query(self):
        assert call(
            f'{INTERP} {self.path_runner} --ai 1rcy'.split(),
            stdout=DEVNULL
        ) == EXIT_SUCCESS

    def test_bridging_interaction_working_query(self):
        assert call(
            f'{INTERP} {self.path_runner} --bi 1rcy'.split(),
            stdout=DEVNULL
        ) == EXIT_SUCCESS

    def test_aromatic_interaction_run_from_parent_directory(self):
        pwd = getcwd()
        chdir(path.dirname(path.dirname(self.path_runner)))
        retval = call(
            f'{INTERP} MetAromatic/runner.py --ai 1rcy'.split(),
            stdout=DEVNULL
        )
        chdir(pwd)
        assert retval == EXIT_SUCCESS

    def test_aromatic_interaction_run_from_child_directory(self):
        pwd = getcwd()
        chdir(path.join(path.dirname(self.path_runner), 'src/'))
        retval = call(
            f'{INTERP} ../runner.py --ai 1rcy'.split(),
            stdout=DEVNULL
        )
        chdir(pwd)
        assert retval == EXIT_SUCCESS

    def test_aromatic_interaction_run_from_child_child_directory(self):
        pwd = getcwd()
        chdir(path.join(path.dirname(self.path_runner), 'src/utilities'))
        retval = call(
            f'{INTERP} ../../runner.py --ai 1rcy'.split(),
            stdout=DEVNULL
        )
        chdir(pwd)
        assert retval == EXIT_SUCCESS

    def test_bridging_interaction_run_from_parent_directory(self):
        pwd = getcwd()
        chdir(path.dirname(path.dirname(self.path_runner)))
        retval = call(
            f'{INTERP} MetAromatic/runner.py --bi 6lu7'.split(),
            stdout=DEVNULL
        )
        chdir(pwd)
        assert retval == EXIT_SUCCESS

    def test_bridging_interaction_run_from_child_directory(self):
        pwd = getcwd()
        chdir(path.join(path.dirname(self.path_runner), 'src/'))
        retval = call(
            f'{INTERP} ../runner.py --bi 6lu7'.split(),
            stdout=DEVNULL
        )
        chdir(pwd)
        assert retval == EXIT_SUCCESS

    def test_bridging_interaction_run_from_child_child_directory(self):
        pwd = getcwd()
        chdir(path.join(path.dirname(self.path_runner), 'src/utilities'))
        retval = call(
            f'{INTERP} ../../runner.py --bi 6lu7'.split(),
            stdout=DEVNULL
        )
        chdir(pwd)
        assert retval == EXIT_SUCCESS

    def test_bridging_interaction_working_query_vertices_3(self):
        assert call(
            f'{INTERP} {self.path_runner} --bi 1rcy --vertices 3'.split(),
            stdout=DEVNULL
        ) == EXIT_SUCCESS

    def test_bridging_interaction_working_query_vertices_2(self):
        assert call(
            f'{INTERP} {self.path_runner} --bi 1rcy --vertices 2'.split(),
            stdout=DEVNULL
        ) == EXIT_FAILURE 

    def test_invalid_cutoff_distance(self):
        assert call(
            f'{INTERP} {self.path_runner} --ai 1rcy --cutoff_distance 0.00'.split(),
            stdout=DEVNULL
        ) == errors.ErrorCodes.InvalidCutoffsError

    def test_invalid_cutoff_distance_stringified(self):
        assert call(
            f'{INTERP} {self.path_runner} --ai 1rcy --cutoff_distance foo'.split(),
            stderr=DEVNULL
        ) == EXIT_GENERAL_PROGRAM_FAILURES

    def test_invalid_cutoff_angle(self):
        assert call(
            f'{INTERP} {self.path_runner} --ai 1rcy --cutoff_angle 361.00'.split(),
            stdout=DEVNULL
        ) == errors.ErrorCodes.InvalidCutoffsError

    def test_invalid_code(self):
        assert call(
            f'{INTERP} {self.path_runner} --ai foobar'.split(),
            stdout=DEVNULL
        ) == errors.ErrorCodes.InvalidPDBFileError

    def test_no_met_coordinates(self):
        assert call(
            f'{INTERP} {self.path_runner} --ai 3nir'.split(),
            stdout=DEVNULL
        ) == errors.ErrorCodes.NoMetCoordinatesError

    def test_invalid_model(self):
        assert call(
            f'{INTERP} {self.path_runner} --ai 1rcy --model foobarbaz'.split(),
            stdout=DEVNULL
        ) == errors.ErrorCodes.InvalidModelError

    def test_no_results(self):
        assert call(
            f'{INTERP} {self.path_runner} --ai 1a5r'.split(),
            stdout=DEVNULL
        ) == errors.ErrorCodes.NoResultsError

    def test_bad_query_type(self):
        assert call(
            f'{INTERP} {self.path_runner} --ai 1rcy --query foobarbaz'.split(),
            stderr=DEVNULL
        ) == EXIT_GENERAL_PROGRAM_FAILURES

    @mark.skipif('Windows' in system(), reason='Python 2 path cannot be resolved on Windows.')
    def test_exit_with_python_2(self):
        assert call(
            f'python2 {self.path_runner} --ai 1rcy'.split(),
            stdout=DEVNULL,
            stderr=DEVNULL
        ) == EXIT_FAILURE

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
    def test_general_argparse_failures(self, subquery):
        assert call(
            f'{INTERP} {self.path_runner} {subquery}'.split(),
            stderr=DEVNULL
        ) == EXIT_GENERAL_PROGRAM_FAILURES
