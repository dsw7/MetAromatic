from os import path, chdir, getcwd
from subprocess import call, DEVNULL
from pytest import mark
from consts import (
    EXIT_SUCCESS,
    EXIT_FAILURE,
    EXIT_GENERAL_PROGRAM_FAILURES
)


class TestCommandLineInterface:
    def setup_class(self):
        root = path.dirname(path.dirname(path.abspath(__file__)))
        self.path_runner = path.join(root, 'runner.py')

    def test_aromatic_interaction_working_query(self):
        assert call(
            f'{self.path_runner} single-met-aromatic-query 1rcy'.split(),
            stdout=DEVNULL
        ) == EXIT_SUCCESS

    def test_bridging_interaction_working_query(self):
        assert call(
            f'{self.path_runner} single-bridging-interaction-query 1rcy'.split(),
            stdout=DEVNULL
        ) == EXIT_SUCCESS

    def test_aromatic_interaction_run_from_parent_directory(self):
        pwd = getcwd()
        chdir(path.dirname(path.dirname(self.path_runner)))
        retval = call(
            f'MetAromatic/runner.py single-met-aromatic-query 1rcy'.split(),
            stdout=DEVNULL
        )
        chdir(pwd)
        assert retval == EXIT_SUCCESS

    def test_aromatic_interaction_run_from_child_directory(self):
        pwd = getcwd()
        chdir(path.join(path.dirname(self.path_runner), 'src/'))
        retval = call(
            f'../runner.py single-met-aromatic-query 1rcy'.split(),
            stdout=DEVNULL
        )
        chdir(pwd)
        assert retval == EXIT_SUCCESS

    def test_aromatic_interaction_run_from_child_child_directory(self):
        pwd = getcwd()
        chdir(path.join(path.dirname(self.path_runner), 'src/utilities'))
        retval = call(
            f'../../runner.py single-met-aromatic-query 1rcy'.split(),
            stdout=DEVNULL
        )
        chdir(pwd)
        assert retval == EXIT_SUCCESS

    def test_bridging_interaction_run_from_parent_directory(self):
        pwd = getcwd()
        chdir(path.dirname(path.dirname(self.path_runner)))
        retval = call(
            f'MetAromatic/runner.py single-bridging-interaction-query 6lu7'.split(),
            stdout=DEVNULL
        )
        chdir(pwd)
        assert retval == EXIT_SUCCESS

    def test_bridging_interaction_run_from_child_directory(self):
        pwd = getcwd()
        chdir(path.join(path.dirname(self.path_runner), 'src/'))
        retval = call(
            f'../runner.py single-bridging-interaction-query 6lu7'.split(),
            stdout=DEVNULL
        )
        chdir(pwd)
        assert retval == EXIT_SUCCESS

    def test_bridging_interaction_run_from_child_child_directory(self):
        pwd = getcwd()
        chdir(path.join(path.dirname(self.path_runner), 'src/utilities'))
        retval = call(
            f'../../runner.py single-bridging-interaction-query 6lu7'.split(),
            stdout=DEVNULL
        )
        chdir(pwd)
        assert retval == EXIT_SUCCESS

    def test_bridging_interaction_working_query_vertices_3(self):
        assert call(
            f'{self.path_runner} single-bridging-interaction-query 1rcy --vertices 3'.split(),
            stdout=DEVNULL
        ) == EXIT_SUCCESS

    def test_bridging_interaction_working_query_vertices_2(self):
        assert call(
            f'{self.path_runner} single-bridging-interaction-query 1rcy --vertices 2'.split(),
            stdout=DEVNULL
        ) == EXIT_FAILURE

    def test_invalid_cutoff_distance(self):
        assert call(
            f'{self.path_runner} single-met-aromatic-query 1rcy --cutoff-distance 0.00'.split(),
            stdout=DEVNULL
        ) == EXIT_FAILURE

    def test_invalid_cutoff_distance_stringified(self):
        assert call(
            f'{self.path_runner} single-met-aromatic-query 1rcy --cutoff-distance foo'.split(),
            stderr=DEVNULL
        ) == EXIT_GENERAL_PROGRAM_FAILURES

    def test_invalid_cutoff_angle(self):
        assert call(
            f'{self.path_runner} single-met-aromatic-query 1rcy --cutoff-angle 361.00'.split(),
            stdout=DEVNULL
        ) == EXIT_FAILURE

    def test_invalid_code(self):
        assert call(
            f'{self.path_runner} single-met-aromatic-query foobar'.split(),
            stdout=DEVNULL
        ) == EXIT_FAILURE

    def test_no_met_coordinates(self):
        assert call(
            f'{self.path_runner} single-met-aromatic-query 3nir'.split(),
            stdout=DEVNULL
        ) == EXIT_FAILURE

    def test_invalid_model(self):
        assert call(
            f'{self.path_runner} single-met-aromatic-query 1rcy --model foobarbaz'.split(),
            stdout=DEVNULL
        ) == EXIT_FAILURE

    def test_no_results(self):
        assert call(
            f'{self.path_runner} single-met-aromatic-query 1a5r'.split(),
            stdout=DEVNULL
        ) == EXIT_FAILURE

    def test_bad_query_type(self):
        assert call(
            f'{self.path_runner} single-met-aromatic-query 1rcy --query foobarbaz'.split(),
            stderr=DEVNULL
        ) == EXIT_GENERAL_PROGRAM_FAILURES

    @mark.parametrize(
        'subquery',
        [
            'single-met-aromatic-query ',
            'single-met-aromatic-query 1rcy single-bridging-interaction-query 1rcy',
            'single-met-aromatic-query 1rcy --cutoff-distance foobar',
            'single-met-aromatic-query 1rcy --cutoff-angle foobar',
            'single-met-aromatic-query 1rcy --vertices foo',
            '--batch ',
        ]
    )
    def test_general_argparse_failures(self, subquery):
        assert call(
            f'{self.path_runner} {subquery}'.split(),
            stderr=DEVNULL
        ) == EXIT_GENERAL_PROGRAM_FAILURES
