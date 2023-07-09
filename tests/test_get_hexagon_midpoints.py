from MetAromatic.get_aromatic_midpoints import get_midpoints

HEXAGON_COORDINATES = [0.866, 0.866, 0.0, -0.866, -0.866, 0.0]
HEXAGON_MIDPOINTS = [0.866, 0.433, -0.433, -0.866, -0.433, 0.433]

def test_get_hexagon_midpoints() -> None:
    assert get_midpoints(HEXAGON_COORDINATES) == HEXAGON_MIDPOINTS
