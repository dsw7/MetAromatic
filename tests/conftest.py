from pathlib import Path
from click.testing import CliRunner
from pytest import fixture
from MetAromatic.models import MetAromaticParams


@fixture(scope="session")
def ma_params() -> MetAromaticParams:
    return MetAromaticParams(
        cutoff_distance=4.9, cutoff_angle=109.5, chain="A", model="cp"
    )


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
