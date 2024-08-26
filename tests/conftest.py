from pathlib import Path
from pytest import fixture


@fixture
def resources() -> Path:
    return Path(__file__).resolve().parent / "resources"


@fixture
def pdb_file_1rcy(resources: Path) -> Path:
    # A valid PDB file
    return resources / "data_1rcy.pdb"


@fixture
def pdb_file_invalid(resources: Path) -> Path:
    # An invalid PDB file
    return resources / "data_lorem_ipsum.pdb"
