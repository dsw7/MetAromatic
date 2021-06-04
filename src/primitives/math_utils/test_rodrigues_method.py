# pylint: disable=W0201  # Disable "Attribute defined outside __init__"

from numpy import (
    array,
    around,
    array_equal
)
from .rodrigues_method import RodriguesMethod

class TestRodriguesMethod:

    def setup_class(self) -> None:
        vertex_a = array([0.5, 0.5, 0.0])
        vertex_g = array([0.5, -0.5, 0.0])
        origin = array([0.0, 0.0, 0.0])

        self.frame_rm = RodriguesMethod(
            vertex_a, origin, vertex_g
        )

    def test_rm_vector_a(self) -> None:
        assert array_equal(around(self.frame_rm.get_vector_a(), decimals=1), [-0.5, 0.0, -0.5])

    def test_rm_vector_g(self) -> None:
        assert array_equal(around(self.frame_rm.get_vector_g(), decimals=1), [-0.5, 0.0, 0.5])
