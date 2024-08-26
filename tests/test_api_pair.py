from json import loads
from pathlib import Path
from unittest import TestCase
import pytest
from MetAromatic import get_pairs_from_pdb, get_pairs_from_file
from MetAromatic.aliases import Models
from MetAromatic.errors import SearchError
from MetAromatic.models import MetAromaticParams, FeatureSpace, DictInteractions


@pytest.fixture
def ma_params() -> MetAromaticParams:
    return MetAromaticParams(
        cutoff_distance=4.9, cutoff_angle=109.5, chain="A", model="cp"
    )


@pytest.fixture
def valid_results_1rcy(resources: Path) -> list[DictInteractions]:
    return loads((resources / "expected_results_1rcy.json").read_text())


def test_pair_1rcy_valid_results(
    ma_params: MetAromaticParams, valid_results_1rcy: list[DictInteractions]
) -> None:
    fs: FeatureSpace = get_pairs_from_pdb(params=ma_params, pdb_code="1rcy")

    tc = TestCase()
    tc.maxDiff = None
    tc.assertCountEqual(fs.serialize_interactions(), valid_results_1rcy)


def test_pair_1rcy_valid_results_use_local(
    ma_params: MetAromaticParams,
    valid_results_1rcy: list[DictInteractions],
    pdb_file_1rcy: Path,
) -> None:
    fs: FeatureSpace = get_pairs_from_file(params=ma_params, filepath=pdb_file_1rcy)

    tc = TestCase()
    tc.maxDiff = None
    tc.assertCountEqual(fs.serialize_interactions(), valid_results_1rcy)


def test_pair_1rcy_valid_results_use_local_invalid_file(
    ma_params: MetAromaticParams, pdb_file_invalid
) -> None:
    with pytest.raises(SearchError, match="Not a valid PDB file"):
        get_pairs_from_file(params=ma_params, filepath=pdb_file_invalid)


@pytest.mark.parametrize(
    "code, cutoff_distance, cutoff_angle, model, error",
    [
        ("1rcy", -0.01, 109.5, "cp", "Invalid cutoff distance"),
        ("1rcy", 4.95, -60.0, "cp", "Invalid cutoff angle"),
        ("1rcy", 4.95, 720.0, "cp", "Invalid cutoff angle"),
        ("2rcy", 4.95, 109.5, "cp", "No MET residues"),
        ("3nir", 4.95, 109.5, "cp", "No MET residues"),
        ("6mwm", 4.95, 109.5, "cp", "No PHE/TYR/TRP residues"),
        ("abcd", 4.95, 109.5, "cp", "Invalid PDB entry"),
        ("1rcy", 4.95, 109.5, "pc", "Invalid model"),
        ("1rcy", "4.95", 109.5, "cp", "Cutoff distance must be a valid float"),
        ("1rcy", 4.95, "109.5", "cp", "Cutoff angle must be a valid float"),
        ("1rcy", 4.95, 109.5, 25, "Model must be a valid string"),
    ],
)
def test_pair_invalid_inputs(
    code: str,
    cutoff_distance: float,
    cutoff_angle: float,
    model: Models,  # Note the 'pc' passed above would technically fail type checker
    error: str,
) -> None:
    with pytest.raises(SearchError, match=error):
        get_pairs_from_pdb(
            pdb_code=code,
            params=MetAromaticParams(
                cutoff_angle=cutoff_angle,
                cutoff_distance=cutoff_distance,
                chain="A",
                model=model,
            ),
        )


def test_pair_no_results_error(ma_params: MetAromaticParams) -> None:
    with pytest.raises(SearchError, match="No Met-aromatic interactions"):
        get_pairs_from_pdb(params=ma_params, pdb_code="1a5r")
