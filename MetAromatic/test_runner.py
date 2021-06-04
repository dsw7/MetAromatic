from click.testing import CliRunner
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


"""
    def test_invalid_cutoff_angle(self):
        assert call(
            f'{self.path_runner} pair 1rcy --cutoff-angle 361.00'.split(),
            stdout=DEVNULL
        ) == EXIT_FAILURE

    def test_invalid_code(self):
        assert call(
            f'{self.path_runner} pair foobar'.split(),
            stdout=DEVNULL
        ) == EXIT_FAILURE

    def test_no_met_coordinates(self):
        assert call(
            f'{self.path_runner} pair 3nir'.split(),
            stdout=DEVNULL
        ) == EXIT_FAILURE

    def test_invalid_model(self):
        assert call(
            f'{self.path_runner} pair 1rcy --model foobarbaz'.split(),
            stdout=DEVNULL
        ) == EXIT_FAILURE

    def test_no_results(self):
        assert call(
            f'{self.path_runner} pair 1a5r'.split(),
            stdout=DEVNULL
        ) == EXIT_FAILURE

    def test_bad_query_type(self):
        assert call(
            f'{self.path_runner} pair 1rcy --query foobarbaz'.split(),
            stderr=DEVNULL
        ) == EXIT_GENERAL_PROGRAM_FAILURES

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
        assert call(
            f'{self.path_runner} {subquery}'.split(),
            stderr=DEVNULL
        ) == EXIT_GENERAL_PROGRAM_FAILURES
"""
