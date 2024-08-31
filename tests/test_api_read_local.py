from pathlib import Path
import pytest
from utils import compare_interactions, Defaults
from MetAromatic import get_pairs_from_file
from MetAromatic.aliases import Models
from MetAromatic.errors import SearchError
from MetAromatic.models import FeatureSpace, DictInteractions


@pytest.fixture
def pdb_file_invalid(resources: Path) -> Path:
    return resources / "data_lorem_ipsum.pdb"


def test_pair_1rcy_valid_results_use_local(
    defaults: Defaults,
    valid_results_1rcy: list[DictInteractions],
    pdb_file_1rcy: Path,
) -> None:
    fs: FeatureSpace = get_pairs_from_file(filepath=pdb_file_1rcy, **defaults)
    compare_interactions(fs.serialize_interactions(), valid_results_1rcy)


def test_pair_1rcy_valid_results_use_local_invalid_file(
    defaults: Defaults, pdb_file_invalid: Path
) -> None:
    with pytest.raises(SearchError, match="Not a valid PDB file"):
        get_pairs_from_file(filepath=pdb_file_invalid, **defaults)


@pytest.mark.parametrize(
    "cutoff_distance, cutoff_angle, model, error",
    [
        (-0.01, 109.5, "cp", "cutoff_distance: Input should be greater than 0"),
        (4.95, -60.0, "cp", "cutoff_angle: Input should be greater than 0"),
        (4.95, 720.0, "cp", "cutoff_angle: Input should be less than or equal to 360"),
        (4.95, 109.5, "pc", "model: Input should be 'cp' or 'rm'"),
        ("4.95", 109.5, "cp", "cutoff_distance: Input should be a valid number"),
        (4.95, "109.5", "cp", "cutoff_angle: Input should be a valid number"),
        (4.95, 109.5, 25, "model: Input should be 'cp' or 'rm'"),
    ],
)
def test_read_local_validation(
    cutoff_angle: float,
    cutoff_distance: float,
    error: str,
    model: Models,  # Note the 'pc' passed above would technically fail type checker
    pdb_file_1rcy: Path,
) -> None:
    with pytest.raises(SearchError, match=error):
        get_pairs_from_file(
            filepath=pdb_file_1rcy,
            cutoff_angle=cutoff_angle,
            cutoff_distance=cutoff_distance,
            chain="A",
            model=model,
        )
