from os import EX_OK
from click.testing import CliRunner
from pytest import mark
from MetAromatic.runner import cli


def test_pair_working_query(cli_runner: CliRunner) -> None:
    command = "pair 1rcy"
    result = cli_runner.invoke(cli, command.split())
    assert result.exit_code == EX_OK


def test_pair_working_query_with_options(cli_runner: CliRunner) -> None:
    command = (
        "--cutoff-distance 6.0 --cutoff-angle 109.5 --model rm --chain A pair 1rcy"
    )
    result = cli_runner.invoke(cli, command.split())
    assert result.exit_code == EX_OK


def test_pair_invalid_cutoff_distance(cli_runner: CliRunner) -> None:
    command = "--cutoff-distance -1.00 pair 1rcy"
    result = cli_runner.invoke(cli, command.split())

    assert result.exit_code != EX_OK
    assert "Invalid value for '--cutoff-distance'" in result.output


def test_pair_invalid_cutoff_distance_stringified(cli_runner: CliRunner) -> None:
    command = "--cutoff-distance foo pair 1rcy"
    result = cli_runner.invoke(cli, command.split())

    assert result.exit_code != EX_OK
    assert "Invalid value for '--cutoff-distance'" in result.output


def test_pair_invalid_cutoff_angle(cli_runner: CliRunner) -> None:
    command = "--cutoff-angle 361.00 pair 1rcy"
    result = cli_runner.invoke(cli, command.split())

    assert result.exit_code != EX_OK
    assert "Invalid value for '--cutoff-angle'" in result.output


def test_pair_invalid_code(cli_runner: CliRunner) -> None:
    command = "pair foobar"
    result = cli_runner.invoke(cli, command.split())

    assert result.exit_code != EX_OK


def test_pair_no_met_residues(cli_runner: CliRunner) -> None:
    command = "pair 3nir"
    result = cli_runner.invoke(cli, command.split())

    assert result.exit_code != EX_OK
    assert "No MET residues\n" in result.output


def test_pair_invalid_model(cli_runner: CliRunner) -> None:
    command = "--model foobar pair 1rcy"
    result = cli_runner.invoke(cli, command.split())

    assert result.exit_code != EX_OK
    assert "Invalid value for '--model'" in result.output


def test_pair_no_results(cli_runner: CliRunner) -> None:
    command = "pair 1a5r"

    result = cli_runner.invoke(cli, command.split())
    assert result.exit_code != EX_OK
    assert "No Met-aromatic interactions" in result.output


def test_pair_bad_query_type(cli_runner: CliRunner) -> None:
    command = "--query foobar pair 1rcy"

    result = cli_runner.invoke(cli, command.split())
    assert result.exit_code != EX_OK


@mark.parametrize(
    "subquery",
    [
        "pair ",
        "pair 1rcy bridge 1rcy",
        "pair 1rcy --cutoff-distance foobar",
        "pair 1rcy --cutoff-angle foobar",
        "pair 1rcy --vertices foo",
        "--batch ",
    ],
)
def test_general_argparse_failures(cli_runner: CliRunner, subquery: str) -> None:
    result = cli_runner.invoke(cli, subquery.split())
    assert result.exit_code != EX_OK
