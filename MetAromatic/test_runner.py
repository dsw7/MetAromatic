from pathlib import Path
from os import chdir, getcwd, EX_OK
from subprocess import call, DEVNULL
from contextlib import contextmanager
from click.testing import CliRunner
from pytest import mark
from runner import cli

TEST_DATA = Path(__file__).resolve().parent / 'core' / 'test_data' / 'data_coronavirus_entries.txt'
DB_NAME = 'database_coronavirus'
COL_NAME = 'collection_coronavirus'

@contextmanager
def restore_original_dir():

    original_pwd = getcwd()

    try:
        yield
    finally:
        chdir(original_pwd)


@mark.test_command_line_interface
class TestRunner:

    def setup_class(self):
        self.runner = CliRunner()

    def test_pair_working_query(self):
        command = 'pair 1rcy'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EX_OK

    def test_pair_working_query_with_options(self):
        command = '--cutoff-distance 6.0 --cutoff-angle 109.5 --model rm --chain A pair 1rcy'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EX_OK

    def test_bridge_working_query_vertices_3(self):
        command = 'bridge 1rcy --vertices 3'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EX_OK

    def test_bridge_working_query_with_options(self):
        command = '--cutoff-distance 6.0 --cutoff-angle 109.5 --model rm --chain A bridge 6lu7'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EX_OK

    def test_bridge_working_query_vertices_2(self):
        command = 'bridge 1rcy --vertices 2'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK
        assert result.output == 'Vertices must be >= 3\n'

    def test_bridge_with_cutoff_distance(self):
        command = '--cutoff-distance 7.0 bridge 6lu7'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EX_OK

    def test_bridge_with_cutoff_angle(self):
        command = '--cutoff-angle 75 bridge 6lu7'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EX_OK

    def test_invalid_cutoff_distance(self):
        command = '--cutoff-distance -1.00 pair 1rcy'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK
        assert result.output == 'Invalid cutoff distance\nExited with code: 1\n'

    def test_invalid_cutoff_distance_stringified(self):
        command = '--cutoff-distance foo pair 1rcy'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK

    def test_invalid_cutoff_angle(self):
        command = '--cutoff-angle 361.00 pair 1rcy'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK

    def test_invalid_code(self):
        command = 'pair foobar'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK

    def test_no_met_coordinates(self):
        command = 'pair 3nir'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK
        assert result.output == 'No MET residues\nExited with code: 1\n'

    def test_invalid_model_pair(self):
        command = '--model foobar pair 1rcy'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK
        assert result.output == 'Invalid model\nExited with code: 1\n'

    def test_invalid_model_bridge(self):
        command = '--model foobar bridge 6lu7'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK
        assert result.output == 'Invalid model\nExited with code: 1\n'

    def test_no_results(self):
        command = 'pair 1a5r'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK
        assert result.output == 'No interactions\nExited with code: 1\n'

    def test_bad_query_type(self):
        command = '--query foobar pair 1rcy'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK

    def test_batch_too_few_threads(self):
        command = f'batch {TEST_DATA} --threads=-1 --database={DB_NAME} --collection={COL_NAME}'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK

    def test_batch_too_many_threads(self):
        command = f'batch {TEST_DATA} --threads=100 --database={DB_NAME} --collection={COL_NAME}'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK

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
        assert result.exit_code != EX_OK


@mark.test_command_line_interface
class TestRunFromDifferentDirectories:

    def setup_class(self):
        self.root = Path(__file__).resolve().parent

    def test_aromatic_interaction_run_from_parent_directory(self):

        with restore_original_dir():
            chdir(self.root.parent)
            exit_code = call('MetAromatic/runner.py pair 1rcy'.split(), stdout=DEVNULL)

            assert exit_code == EX_OK

    def test_aromatic_interaction_run_from_child_directory(self):

        with restore_original_dir():
            chdir(self.root / 'core')
            exit_code = call('../runner.py pair 1rcy'.split(), stdout=DEVNULL)

            assert exit_code == EX_OK

    def test_bridging_interaction_run_from_parent_directory(self):

        with restore_original_dir():
            chdir(self.root.parent)
            exit_code = call('MetAromatic/runner.py bridge 6lu7'.split(), stdout=DEVNULL)

            assert exit_code == EX_OK

    def test_bridging_interaction_run_from_child_directory(self):

        with restore_original_dir():
            chdir(self.root / 'core')
            exit_code = call('../runner.py bridge 6lu7'.split(), stdout=DEVNULL)

            assert exit_code == EX_OK
