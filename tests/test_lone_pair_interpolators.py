# pylint: disable=W0201  # Disable "Attribute defined outside __init__"

from numpy import array, around, array_equal
from MetAromatic.lone_pair_interpolators import CrossProductMethod, RodriguesMethod

VERTEX_A = array([0.5, 0.5, 0.0])
VERTEX_G = array([0.5, -0.5, 0.0])
ORIGIN = array([0.0, 0.0, 0.0])


class TestCrossProductMethod:

    def setup_class(self) -> None:
        self.frame_cp = CrossProductMethod(VERTEX_A, ORIGIN, VERTEX_G)

    def test_cp_vector_a(self) -> None:
        assert array_equal(around(self.frame_cp.get_vector_a(), decimals=2), [-1., 0., -1.41])

    def test_cp_vector_g(self) -> None:
        assert array_equal(around(self.frame_cp.get_vector_g(), decimals=2), [-1., 0., 1.41])


class TestRodriguesMethod:

    def setup_class(self) -> None:
        self.frame_rm = RodriguesMethod(VERTEX_A, ORIGIN, VERTEX_G)

    def test_rm_vector_a(self) -> None:
        assert array_equal(around(self.frame_rm.get_vector_a(), decimals=1), [-0.5, 0.0, -0.5])

    def test_rm_vector_g(self) -> None:
        assert array_equal(around(self.frame_rm.get_vector_g(), decimals=1), [-0.5, 0.0, 0.5])
