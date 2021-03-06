from .get_hexagon_midpoints import get_hexagon_midpoints

HEXAGON_COORDINATES = [
    (0.866, 0.5, 0.0),
    (0.866, -0.5, 0.0),
    (0.0, -1.0, 0.0),
    (-0.866, -0.5, 0.0),
    (-0.866, 0.5, 0.0),
    (0.0, 1.0, 0.0)
]

HEXAGON_MIDPOINTS = {
    (0.433, 0.75, 0.0),
    (-0.433, 0.75, 0.0),
    (-0.866, 0.0, 0.0),
    (-0.433, -0.75, 0.0),
    (0.433, -0.75, 0.0),
    (0.866, 0.0, 0.0)
}

def test_get_hexagon_midpoints():
    coordinates = [list(i) for i in zip(*HEXAGON_COORDINATES)]
    assert {
        tuple(i) for i in zip(*get_hexagon_midpoints(*coordinates))
    } == HEXAGON_MIDPOINTS
