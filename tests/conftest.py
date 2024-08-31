from json import loads
from pathlib import Path
from click.testing import CliRunner
from pytest import fixture
from utils import Defaults
from MetAromatic.models import DictInteractions


@fixture(scope="session")
def defaults() -> Defaults:
    return Defaults(cutoff_distance=4.9, cutoff_angle=109.5, chain="A", model="cp")


@fixture(scope="session")
def cli_runner() -> CliRunner:
    return CliRunner()


@fixture(scope="session")
def resources() -> Path:
    return Path(__file__).resolve().parent / "resources"


@fixture(scope="session")
def pdb_file_1rcy(resources: Path) -> Path:
    # A valid PDB file
    return resources / "data_1rcy.pdb"


@fixture(scope="session")
def valid_results_1rcy(resources: Path) -> list[DictInteractions]:
    raw_results: str = (resources / "expected_results_1rcy.json").read_text()

    results: list[DictInteractions] = loads(raw_results)
    return results
