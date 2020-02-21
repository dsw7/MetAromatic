from numpy import array, around, array_equal
from .cross_product_method import CrossProductMethod


def test_rodrigues_method():
    vertex_a = array([0.5, 0.5, 0.0])
    vertex_g = array([0.5, -0.5, 0.0])
    origin = array([0.0, 0.0, 0.0])
    frame = CrossProductMethod(vertex_a, origin, vertex_g)
    assert array_equal(around(frame.get_vector_a(), decimals=2), [-1., 0., -1.41])
    assert array_equal(around(frame.get_vector_g(), decimals=2), [-1., 0., 1.41])
