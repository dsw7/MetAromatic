import pytest
from utils import Defaults
from MetAromatic import get_bridges
from MetAromatic.aliases import Models
from MetAromatic.errors import SearchError


@pytest.mark.parametrize(
    "code, error",
    [
        ("2rcy", "No MET residues"),
        ("3nir", "No MET residues"),
        ("6mwm", "No PHE/TYR/TRP residues"),
    ],
)
def test_bridge_missing_residues(code: str, error: str, defaults: Defaults) -> None:
    with pytest.raises(SearchError, match=error):
        get_bridges(code=code, vertices=4, **defaults)


def test_bridge_invalid_pdb_code(defaults: Defaults) -> None:
    with pytest.raises(SearchError, match="Invalid PDB entry"):
        get_bridges(code="abcd", vertices=4, **defaults)


@pytest.mark.parametrize(
    "code, distance, angle, model, error",
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
def test_bridge_validation(
    code: str, distance: float, angle: float, model: Models, error: str
) -> None:
    with pytest.raises(SearchError, match=error):
        get_bridges(
            code=code,
            cutoff_angle=angle,
            cutoff_distance=distance,
            chain="A",
            model=model,
            vertices=4,
        )


@pytest.mark.parametrize(
    "code, error",
    [("1a5r", "No Met-aromatic interactions"), ("1rcy", "Found no bridges")],
)
def test_no_results(code: str, error: str, defaults: Defaults) -> None:
    with pytest.raises(SearchError, match=error):
        get_bridges(code=code, vertices=4, **defaults)
