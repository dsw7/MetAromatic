from os import EX_OK
from click.testing import CliRunner
from MetAromatic.runner import cli


def test_bridge_working_query_vertices_3(cli_runner: CliRunner) -> None:
    command = "bridge 1rcy --vertices 3"

    result = cli_runner.invoke(cli, command.split())
    assert result.exit_code == EX_OK
    assert "Found 0 bridges" in result.output


def test_bridge_working_query_with_options(cli_runner: CliRunner) -> None:
    command = (
        "--cutoff-distance 6.0 --cutoff-angle 109.5 --model rm --chain A bridge 6lu7"
    )

    result = cli_runner.invoke(cli, command.split())
    assert result.exit_code == EX_OK


def test_bridge_working_query_vertices_2(cli_runner: CliRunner) -> None:
    command = "bridge 1rcy --vertices 2"

    result = cli_runner.invoke(cli, command.split())
    assert result.exit_code != EX_OK
    assert "Invalid value for '--vertices'" in result.output


def test_bridge_with_cutoff_distance(cli_runner: CliRunner) -> None:
    command = "--cutoff-distance 7.0 bridge 6lu7"

    result = cli_runner.invoke(cli, command.split())
    assert result.exit_code == EX_OK


def test_bridge_with_cutoff_angle(cli_runner: CliRunner) -> None:
    command = "--cutoff-angle 75 bridge 6lu7"

    result = cli_runner.invoke(cli, command.split())
    assert result.exit_code == EX_OK


def test_bridge_invalid_model(cli_runner: CliRunner) -> None:
    command = "--model foobar bridge 6lu7"

    result = cli_runner.invoke(cli, command.split())
    assert result.exit_code != EX_OK
    assert "Invalid value for '--model'" in result.output
