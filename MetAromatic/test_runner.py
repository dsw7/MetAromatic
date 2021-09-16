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
from core.helpers.consts import (
    EXIT_SUCCESS,
    EXIT_FAILURE,
    EXIT_GENERAL_PROGRAM_FAILURES
)


class TestRunner:

    def setup_class(self):
        self.runner = CliRunner()

    def test_pair_working_query(self):
        command = 'pair 1rcy'
        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EXIT_SUCCESS

    def test_pair_working_query_with_options(self):
        command = '--cutoff-distance 6.0 --cutoff-angle 109.5 --model rm --chain A pair 1rcy'
        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EXIT_SUCCESS

    def test_bridge_working_query_vertices_3(self):
        command = 'bridge 1rcy --vertices 3'
        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EXIT_SUCCESS

    def test_bridge_working_query_with_options(self):
        command = '--cutoff-distance 6.0 --cutoff-angle 109.5 --model rm --chain A bridge 6lu7'
        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EXIT_SUCCESS

    def test_bridge_working_query_vertices_2(self):
        command = 'bridge 1rcy --vertices 2'
        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EXIT_FAILURE
        assert result.output == 'Vertices must be >= 3\n'

    def test_bridge_with_cutoff_distance(self):
        command = '--cutoff-distance 7.0 bridge 6lu7'
        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EXIT_SUCCESS

    def test_bridge_with_cutoff_angle(self):
        command = '--cutoff-angle 75 bridge 6lu7'
        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EXIT_SUCCESS

    def test_invalid_cutoff_distance(self):
        command = '--cutoff-distance -1.00 pair 1rcy'
        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EXIT_FAILURE
        assert result.output == 'Invalid cutoff distance\nExited with code: 1\n'

    def test_invalid_cutoff_distance_stringified(self):
        command = '--cutoff-distance foo pair 1rcy'
        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EXIT_GENERAL_PROGRAM_FAILURES

    def test_invalid_cutoff_angle(self):
        command = '--cutoff-angle 361.00 pair 1rcy'
        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EXIT_FAILURE

    def test_invalid_code(self):
        command = 'pair foobar'
        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EXIT_FAILURE

    def test_no_met_coordinates(self):
        command = 'pair 3nir'
        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EXIT_FAILURE
        assert result.output == 'No MET residues\nExited with code: 1\n'

    def test_invalid_model_pair(self):
        command = '--model foobar pair 1rcy'
        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EXIT_FAILURE
        assert result.output == 'Invalid model\nExited with code: 1\n'

    def test_invalid_model_bridge(self):
        command = '--model foobar bridge 6lu7'
        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EXIT_FAILURE
        assert result.output == 'Invalid model\nExited with code: 1\n'

    def test_no_results(self):
        command = 'pair 1a5r'
        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EXIT_FAILURE
        assert result.output == 'No interactions\nExited with code: 1\n'

    def test_bad_query_type(self):
        command = '--query foobar pair 1rcy'
        result = self.runner.invoke(cli, command.split())
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
        # XXX amazing place for a __enter__ / __exit__ context
        pwd = getcwd()
        chdir(path.dirname(path.dirname(self.path_runner)))
        retval = call('MetAromatic/runner.py pair 1rcy'.split(), stdout=DEVNULL)
        chdir(pwd)
        assert retval == EXIT_SUCCESS

    def test_aromatic_interaction_run_from_child_directory(self):
        pwd = getcwd()
        chdir(path.join(path.dirname(self.path_runner), 'core/'))
        retval = call('../runner.py pair 1rcy'.split(), stdout=DEVNULL)
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
        chdir(path.join(path.dirname(self.path_runner), 'core/'))
        retval = call('../runner.py bridge 6lu7'.split(), stdout=DEVNULL)
        chdir(pwd)
        assert retval == EXIT_SUCCESS
