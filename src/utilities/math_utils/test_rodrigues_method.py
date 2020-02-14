from numpy import array, around, array_equal
from .rodrigues_method import RodriguesMethod


def test_rodrigues_method():
    vertex_a = array([0.5, 0.5, 0.0])
    vertex_g = array([0.5, -0.5, 0.0])
    origin = array([0.0, 0.0, 0.0])
    frame = RodriguesMethod(vertex_a, origin, vertex_g)
    assert array_equal(around(frame.get_vector_a(), decimals=1), [-0.5, 0.0, -0.5])
    assert array_equal(around(frame.get_vector_g(), decimals=1), [-0.5, 0.0, 0.5])
