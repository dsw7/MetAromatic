from pathlib import Path
from typing import Literal
from unittest import TestCase
import pytest
from MetAromatic import get_pairs_from_pdb, get_pairs_from_file
from MetAromatic.aliases import Models
from MetAromatic.errors import SearchError
from MetAromatic.models import MetAromaticParams, FeatureSpace


@pytest.fixture
def test_params() -> MetAromaticParams:
    return MetAromaticParams(
        cutoff_distance=4.9, cutoff_angle=109.5, chain="A", model="cp"
    )


VALID_RESULTS_1RCY = [
    {
        "aromatic_residue": "TYR",
        "aromatic_position": 122,
        "methionine_position": 18,
        "norm": 4.211,
        "met_theta_angle": 75.766,
        "met_phi_angle": 64.317,
    },
    {
        "aromatic_residue": "TYR",
        "aromatic_position": 122,
        "methionine_position": 18,
        "norm": 3.954,
        "met_theta_angle": 60.145,
        "met_phi_angle": 68.352,
    },
    {
        "aromatic_residue": "TYR",
        "aromatic_position": 122,
        "methionine_position": 18,
        "norm": 4.051,
        "met_theta_angle": 47.198,
        "met_phi_angle": 85.151,
    },
    {
        "aromatic_residue": "TYR",
        "aromatic_position": 122,
        "methionine_position": 18,
        "norm": 4.39,
        "met_theta_angle": 53.4,
        "met_phi_angle": 95.487,
    },
    {
        "aromatic_residue": "TYR",
        "aromatic_position": 122,
        "methionine_position": 18,
        "norm": 4.62,
        "met_theta_angle": 68.452,
        "met_phi_angle": 90.771,
    },
    {
        "aromatic_residue": "TYR",
        "aromatic_position": 122,
        "methionine_position": 18,
        "norm": 4.537,
        "met_theta_angle": 78.568,
        "met_phi_angle": 76.406,
    },
    {
        "aromatic_residue": "PHE",
        "aromatic_position": 54,
        "methionine_position": 148,
        "norm": 4.777,
        "met_theta_angle": 105.947,
        "met_phi_angle": 143.022,
    },
    {
        "aromatic_residue": "PHE",
        "aromatic_position": 54,
        "methionine_position": 148,
        "norm": 4.61,
        "met_theta_angle": 93.382,
        "met_phi_angle": 156.922,
    },
    {
        "aromatic_residue": "PHE",
        "aromatic_position": 54,
        "methionine_position": 148,
        "norm": 4.756,
        "met_theta_angle": 93.287,
        "met_phi_angle": 154.63,
    },
]


def test_pair_1rcy_valid_results(test_params: MetAromaticParams) -> None:
    fs: FeatureSpace = get_pairs_from_pdb(params=test_params, pdb_code="1rcy")

    tc = TestCase()
    tc.maxDiff = None
    tc.assertCountEqual(fs.serialize_interactions(), VALID_RESULTS_1RCY)


def test_pair_1rcy_valid_results_use_local(test_params: MetAromaticParams) -> None:
    # File downloaded from RSCB PDB
    path_pdb_file = Path(__file__).resolve().parent / "data_1rcy.pdb"

    fs: FeatureSpace = get_pairs_from_file(params=test_params, filepath=path_pdb_file)

    tc = TestCase()
    tc.maxDiff = None
    tc.assertCountEqual(fs.serialize_interactions(), VALID_RESULTS_1RCY)


def test_pair_1rcy_valid_results_use_local_invalid_file(
    test_params: MetAromaticParams,
) -> None:
    # Simulating someone passing a non-PDB formatted file into program
    path_pdb_file = Path(__file__).resolve().parent / "data_lorem_ipsum.pdb"

    with pytest.raises(SearchError, match="Not a valid PDB file"):
        get_pairs_from_file(params=test_params, filepath=path_pdb_file)


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
    params = MetAromaticParams(
        cutoff_angle=cutoff_angle,
        cutoff_distance=cutoff_distance,
        chain="A",
        model=model,
    )
    with pytest.raises(SearchError, match=error):
        get_pairs_from_pdb(params=params, pdb_code=code)


def test_pair_no_results_error(test_params: MetAromaticParams) -> None:
    with pytest.raises(SearchError, match="No Met-aromatic interactions"):
        get_pairs_from_pdb(params=test_params, pdb_code="1a5r")
