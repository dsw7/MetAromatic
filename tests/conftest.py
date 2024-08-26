from pathlib import Path
from pytest import fixture


@fixture
def resources() -> Path:
    return Path(__file__).resolve().parent / "resources"
