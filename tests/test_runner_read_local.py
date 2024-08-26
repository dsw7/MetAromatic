from os import EX_OK
from pathlib import Path
from click.testing import CliRunner
from MetAromatic.runner import cli


def test_read_local(cli_runner: CliRunner, pdb_file_1rcy: Path) -> None:
    command = f"read-local {pdb_file_1rcy}"

    result = cli_runner.invoke(cli, command.split())
    assert result.exit_code == EX_OK


def test_read_local_missing_file(cli_runner: CliRunner) -> None:
    command = "read-local /tmp/foo/bar/1rcy.pdb"

    result = cli_runner.invoke(cli, command.split())
    assert result.exit_code != EX_OK
    assert "File '/tmp/foo/bar/1rcy.pdb' does not exist." in result.output
