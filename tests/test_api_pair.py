from json import loads
from pathlib import Path
import pytest
from utils import compare_interactions, Defaults
from MetAromatic import get_pairs_from_pdb, get_pairs_from_file
from MetAromatic.aliases import Models
from MetAromatic.errors import SearchError
from MetAromatic.models import MetAromaticParams, FeatureSpace, DictInteractions


@pytest.fixture(scope="module")
def valid_results_1rcy(resources: Path) -> list[DictInteractions]:
    return loads((resources / "expected_results_1rcy.json").read_text())


@pytest.fixture
def pdb_file_invalid(resources: Path) -> Path:
    # An invalid PDB file
    return resources / "data_lorem_ipsum.pdb"


def test_pair_1rcy_valid_results(
    defaults: Defaults, valid_results_1rcy: list[DictInteractions]
) -> None:
    fs: FeatureSpace = get_pairs_from_pdb(pdb_code="1rcy", **defaults)
    compare_interactions(fs.serialize_interactions(), valid_results_1rcy)


def test_pair_1rcy_valid_results_use_local(
    ma_params: MetAromaticParams,
    valid_results_1rcy: list[DictInteractions],
    pdb_file_1rcy: Path,
) -> None:
    fs: FeatureSpace = get_pairs_from_file(params=ma_params, filepath=pdb_file_1rcy)
    compare_interactions(fs.serialize_interactions(), valid_results_1rcy)


def test_pair_1rcy_valid_results_use_local_invalid_file(
    ma_params: MetAromaticParams, pdb_file_invalid
) -> None:
    with pytest.raises(SearchError, match="Not a valid PDB file"):
        get_pairs_from_file(params=ma_params, filepath=pdb_file_invalid)


@pytest.mark.parametrize(
    "code, error",
    [
        ("2rcy", "No MET residues"),
        ("3nir", "No MET residues"),
        ("6mwm", "No PHE/TYR/TRP residues"),
    ],
)
def test_pair_missing_residues(code: str, error: str, defaults: Defaults) -> None:
    with pytest.raises(SearchError, match=error):
        get_pairs_from_pdb(pdb_code=code, **defaults)


def test_pair_no_results_error(defaults: Defaults) -> None:
    with pytest.raises(SearchError, match="No Met-aromatic interactions"):
        get_pairs_from_pdb(pdb_code="1a5r", **defaults)


def test_pair_invalid_pdb_code(defaults: Defaults) -> None:
    with pytest.raises(SearchError, match="Invalid PDB entry"):
        get_pairs_from_pdb(pdb_code="abcd", **defaults)


@pytest.mark.parametrize(
    "code, cutoff_distance, cutoff_angle, model, error",
    [
        ("1rcy", -0.01, 109.5, "cp", "cutoff_distance: Input should be greater than 0"),
        ("1rcy", 4.95, -60.0, "cp", "cutoff_angle: Input should be greater than 0"),
        ("1rcy", 4.95, 720.0, "cp", "cutoff_angle: Input should be less than 360"),
        ("1rcy", 4.95, 109.5, "pc", "model: Input should be 'cp' or 'rm'"),
        (
            "1rcy",
            "4.95",
            109.5,
            "cp",
            "cutoff_distance: Input should be a valid number",
        ),
        ("1rcy", 4.95, "109.5", "cp", "cutoff_angle: Input should be a valid number"),
        ("1rcy", 4.95, 109.5, 25, "model: Input should be 'cp' or 'rm'"),
    ],
)
def test_pair_validation(
    code: str,
    cutoff_distance: float,
    cutoff_angle: float,
    model: Models,  # Note the 'pc' passed above would technically fail type checker
    error: str,
) -> None:
    with pytest.raises(SearchError, match=error):
        get_pairs_from_pdb(
            pdb_code=code,
            cutoff_angle=cutoff_angle,
            cutoff_distance=cutoff_distance,
            chain="A",
            model=model,
        )
