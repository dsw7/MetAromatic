from os import EX_OK
from pathlib import Path
from click.testing import CliRunner
from pytest import mark
from MetAromatic.runner import cli


class TestRunnerPair:

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

    def test_pair_invalid_cutoff_distance(self):
        command = '--cutoff-distance -1.00 pair 1rcy'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK
        assert "Invalid value for '--cutoff-distance'" in result.output

    def test_pair_invalid_cutoff_distance_stringified(self):
        command = '--cutoff-distance foo pair 1rcy'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK
        assert "Invalid value for '--cutoff-distance'" in result.output

    def test_pair_invalid_cutoff_angle(self):
        command = '--cutoff-angle 361.00 pair 1rcy'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK
        assert "Invalid value for '--cutoff-angle'" in result.output

    def test_pair_invalid_code(self):
        command = 'pair foobar'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK

    def test_pair_no_met_coordinates(self):
        command = 'pair 3nir'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK
        assert 'No MET residues\n' in result.output

    def test_pair_invalid_model(self):
        command = '--model foobar pair 1rcy'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK
        assert "Invalid value for '--model'" in result.output

    def test_pair_no_results(self):
        command = 'pair 1a5r'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EX_OK
        assert 'Found no Met-aromatic interactions for entry' in result.output

    def test_pair_bad_query_type(self):
        command = '--query foobar pair 1rcy'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK

    def test_pair_use_local(self):
        path_pdb_file = Path(__file__).resolve().parent / 'data_1rcy.pdb'
        command = f'pair --read-local {path_pdb_file}'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EX_OK

    def test_pair_use_local_missing_file(self):
        command = 'pair --read-local /tmp/foo/bar/1rcy.pdb'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK
        assert 'File "/tmp/foo/bar/1rcy.pdb" does not exist' in result.output

    def test_pair_enable_debug(self):
        command = '--debug pair 1rcy'

        result = self.runner.invoke(cli, command.split())
        assert result.output.count(' D ') > 0

    def test_pair_disable_debug(self):
        command = 'pair 1rcy'

        result = self.runner.invoke(cli, command.split())
        assert result.output.count(' D ') == 0

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
