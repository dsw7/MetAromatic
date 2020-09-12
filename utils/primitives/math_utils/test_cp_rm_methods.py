from numpy import array, around, array_equal
from .cross_product_method import CrossProductMethod
from .rodrigues_method import RodriguesMethod


class TestVectorInterpolators:
    def setup_class(self):
        vertex_a = array([0.5, 0.5, 0.0])
        vertex_g = array([0.5, -0.5, 0.0])
        origin = array([0.0, 0.0, 0.0])

        self.frame_cp = CrossProductMethod(vertex_a, origin, vertex_g)
        self.frame_rm = RodriguesMethod(vertex_a, origin, vertex_g)

    def test_cp_vector_a(self):
        assert array_equal(around(self.frame_cp.get_vector_a(), decimals=2), [-1., 0., -1.41])

    def test_cp_vector_g(self):
        assert array_equal(around(self.frame_cp.get_vector_g(), decimals=2), [-1., 0., 1.41])

    def test_rm_vector_a(self):
        assert array_equal(around(self.frame_rm.get_vector_a(), decimals=1), [-0.5, 0.0, -0.5])

    def test_rm_vector_g(self):
        assert array_equal(around(self.frame_rm.get_vector_g(), decimals=1), [-0.5, 0.0, 0.5])
