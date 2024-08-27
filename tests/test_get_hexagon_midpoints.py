from MetAromatic.get_aromatic_midpoints import get_midpoints


def test_get_hexagon_midpoints() -> None:
    hexagon_coords = [0.866, 0.866, 0.0, -0.866, -0.866, 0.0]
    hexagon_midpoints = [0.866, 0.433, -0.433, -0.866, -0.433, 0.433]

    assert get_midpoints(hexagon_coords) == hexagon_midpoints
