# pylint: disable=W0201  # Disable "Attribute defined outside __init__"

from pytest import mark
from numpy import (
    array,
    around,
    array_equal
)
from .cross_product_method import CrossProductMethod

@mark.test_command_line_interface
class TestCrossProductMethod:

    def setup_class(self) -> None:
        vertex_a = array([0.5, 0.5, 0.0])
        vertex_g = array([0.5, -0.5, 0.0])
        origin = array([0.0, 0.0, 0.0])

        self.frame_cp = CrossProductMethod(
            vertex_a, origin, vertex_g
        )

    def test_cp_vector_a(self) -> None:
        assert array_equal(around(self.frame_cp.get_vector_a(), decimals=2), [-1., 0., -1.41])

    def test_cp_vector_g(self) -> None:
        assert array_equal(around(self.frame_cp.get_vector_g(), decimals=2), [-1., 0., 1.41])
