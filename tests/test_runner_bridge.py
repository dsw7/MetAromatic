from os import EX_OK
from click.testing import CliRunner
from MetAromatic.runner import cli


class TestRunnerBridge:

    def setup_class(self):
        self.runner = CliRunner()

    def test_bridge_working_query_vertices_3(self):
        command = 'bridge 1rcy --vertices 3'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EX_OK
        assert 'Found no bridges' in result.output

    def test_bridge_working_query_with_options(self):
        command = '--cutoff-distance 6.0 --cutoff-angle 109.5 --model rm --chain A bridge 6lu7'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EX_OK

    def test_bridge_working_query_vertices_2(self):
        command = 'bridge 1rcy --vertices 2'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK
        assert "Invalid value for '--vertices'" in result.output

    def test_bridge_with_cutoff_distance(self):
        command = '--cutoff-distance 7.0 bridge 6lu7'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EX_OK

    def test_bridge_with_cutoff_angle(self):
        command = '--cutoff-angle 75 bridge 6lu7'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code == EX_OK

    def test_bridge_invalid_model(self):
        command = '--model foobar bridge 6lu7'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK
        assert "Invalid value for '--model'" in result.output

    def test_bridge_enable_debug(self):
        command = '--debug bridge 1rcy'

        result = self.runner.invoke(cli, command.split())
        assert result.output.count(' D ') > 0

    def test_bridge_disable_debug(self):
        command = 'bridge 1rcy'

        result = self.runner.invoke(cli, command.split())
        assert result.output.count(' D ') == 0
