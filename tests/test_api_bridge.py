import pytest
from MetAromatic import get_bridges
from MetAromatic.errors import SearchError
from MetAromatic.models import MetAromaticParams


@pytest.mark.parametrize(
    "code, distance, angle, model, status",
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
def test_invalid_inputs(
    code: str, distance: float, angle: float, model: str, status: str
) -> None:
    with pytest.raises(SearchError, match=status):
        get_bridges(
            code=code,
            params=MetAromaticParams(
                chain="A",
                cutoff_angle=angle,
                cutoff_distance=distance,
                # Ignore cp | rm string literal check for testing purposes
                model=model,  # type: ignore
            ),
            vertices=4,
        )


@pytest.mark.parametrize(
    "code, message",
    [("1a5r", "No Met-aromatic interactions"), ("1rcy", "Found no bridges")],
)
def test_no_results(code: str, message: str) -> None:
    with pytest.raises(SearchError, match=message):
        get_bridges(
            code=code,
            params=MetAromaticParams(
                chain="A",
                cutoff_angle=109.5,
                cutoff_distance=4.9,
                model="cp",
            ),
            vertices=4,
        )
