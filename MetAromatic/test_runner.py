from os import (
    path,
    chdir,
    getcwd
)
from subprocess import (
    call,
    DEVNULL
)
from click.testing import CliRunner
from pytest import mark
from runner import cli
from utils.primitives.consts import (
    EXIT_SUCCESS,
    EXIT_FAILURE,
    EXIT_GENERAL_PROGRAM_FAILURES
)


class TestRunner:

    def setup_class(self):
        self.runner = CliRunner()

    def test_pair_working_query(self):
        result = self.runner.invoke(cli, ['pair', '1rcy'])
        assert result.exit_code == EXIT_SUCCESS

    def test_bridge_working_query_vertices_3(self):
        result = self.runner.invoke(cli, ['bridge', '1rcy', '--vertices', '3'])
        assert result.exit_code == EXIT_SUCCESS

    def test_bridge_working_query_vertices_2(self):
        result = self.runner.invoke(cli, ['bridge', '1rcy', '--vertices', '2'])
        assert result.exit_code == EXIT_FAILURE
        assert result.output == 'Vertices must be >= 3\n'

    def test_invalid_cutoff_distance(self):
        result = self.runner.invoke(cli, ['pair', '1rcy', '--cutoff-distance', '-1.00'])
        assert result.exit_code == EXIT_FAILURE
        assert result.output == 'Invalid cutoff distance\nExited with code: 1\n'

    def test_invalid_cutoff_distance_stringified(self):
        result = self.runner.invoke(cli, ['pair', '1rcy', '--cutoff-distance', 'foo'])
        assert result.exit_code == EXIT_GENERAL_PROGRAM_FAILURES

    def test_invalid_cutoff_angle(self):
        result = self.runner.invoke(cli, ['pair', '1rcy', '--cutoff-angle', '361.00'])
        assert result.exit_code == EXIT_FAILURE

    def test_invalid_code(self):
        result = self.runner.invoke(cli, ['pair', 'foobar'])
        assert result.exit_code == EXIT_FAILURE

    def test_no_met_coordinates(self):
        result = self.runner.invoke(cli, ['pair', '3nir'])
        assert result.exit_code == EXIT_FAILURE
        assert result.output == 'No MET residues\nExited with code: 1\n'

    def test_invalid_model(self):
        result = self.runner.invoke(cli, ['pair', '1rcy', '--model', 'foobar'])
        assert result.exit_code == EXIT_FAILURE
        assert result.output == 'Invalid model\nExited with code: 1\n'

    def test_no_results(self):
        result = self.runner.invoke(cli, ['pair', '1a5r'])
        assert result.exit_code == EXIT_FAILURE
        assert result.output == 'No interactions\nExited with code: 1\n'

    def test_bad_query_type(self):
        result = self.runner.invoke(cli, ['pair', '1rcy', '--query', 'foobar'])
        assert result.exit_code == EXIT_GENERAL_PROGRAM_FAILURES

    @mark.parametrize(
        'subquery',
        [
            'pair ',
            'pair 1rcy bridge 1rcy',
            'pair 1rcy --cutoff-distance foobar',
            'pair 1rcy --cutoff-angle foobar',
            'pair 1rcy --vertices foo',
            '--batch ',
        ]
    )
    def test_general_argparse_failures(self, subquery):
        result = self.runner.invoke(cli, subquery.split())
        assert result.exit_code == EXIT_GENERAL_PROGRAM_FAILURES


class TestRunFromDifferentDirectories:

    def setup_class(self):
        root = path.dirname(path.abspath(__file__))
        self.path_runner = path.join(root, 'runner.py')

    def test_aromatic_interaction_run_from_parent_directory(self):
        pwd = getcwd()
        chdir(path.dirname(path.dirname(self.path_runner)))
        retval = call('MetAromatic/runner.py pair 1rcy'.split(), stdout=DEVNULL)
        chdir(pwd)
        assert retval == EXIT_SUCCESS

    def test_aromatic_interaction_run_from_child_directory(self):
        pwd = getcwd()
        chdir(path.join(path.dirname(self.path_runner), 'utils/'))
        retval = call('../runner.py pair 1rcy'.split(), stdout=DEVNULL)
        chdir(pwd)
        assert retval == EXIT_SUCCESS

    def test_aromatic_interaction_run_from_child_child_directory(self):
        pwd = getcwd()
        chdir(path.join(path.dirname(self.path_runner), 'utils/primitives'))
        retval = call('../../runner.py pair 1rcy'.split(), stdout=DEVNULL)
        chdir(pwd)
        assert retval == EXIT_SUCCESS

    def test_bridging_interaction_run_from_parent_directory(self):
        pwd = getcwd()
        chdir(path.dirname(path.dirname(self.path_runner)))
        retval = call('MetAromatic/runner.py bridge 6lu7'.split(), stdout=DEVNULL)
        chdir(pwd)
        assert retval == EXIT_SUCCESS

    def test_bridging_interaction_run_from_child_directory(self):
        pwd = getcwd()
        chdir(path.join(path.dirname(self.path_runner), 'utils/'))
        retval = call('../runner.py bridge 6lu7'.split(), stdout=DEVNULL)
        chdir(pwd)
        assert retval == EXIT_SUCCESS

    def test_bridging_interaction_run_from_child_child_directory(self):
        pwd = getcwd()
        chdir(path.join(path.dirname(self.path_runner), 'utils/primitives'))
        retval = call('../../runner.py bridge 6lu7'.split(), stdout=DEVNULL)
        chdir(pwd)
        assert retval == EXIT_SUCCESS
