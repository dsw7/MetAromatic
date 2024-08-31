from dataclasses import dataclass
from numpy import array, around, array_equal, float64
from numpy.typing import NDArray
from pytest import fixture
from MetAromatic.lone_pair_interpolators import CrossProductMethod, RodriguesMethod


@dataclass
class HalfTetrahedron:
    vertex_a: NDArray[float64]
    vertex_g: NDArray[float64]
    origin: NDArray[float64]


@fixture(scope="module")
def half_tetrahedron() -> HalfTetrahedron:
    return HalfTetrahedron(
        vertex_a=array([0.5, 0.5, 0.0]),
        vertex_g=array([0.5, -0.5, 0.0]),
        origin=array([0.0, 0.0, 0.0]),
    )


@fixture(scope="module")
def frame_cp(half_tetrahedron: HalfTetrahedron) -> CrossProductMethod:
    return CrossProductMethod(
        vertex_a=half_tetrahedron.vertex_a,
        vertex_b=half_tetrahedron.vertex_g,
        origin=half_tetrahedron.origin,
    )


@fixture(scope="module")
def frame_rm(half_tetrahedron: HalfTetrahedron) -> RodriguesMethod:
    return RodriguesMethod(
        vertex_a=half_tetrahedron.vertex_a,
        vertex_b=half_tetrahedron.vertex_g,
        origin=half_tetrahedron.origin,
    )


def test_cp_vector_a(frame_cp: CrossProductMethod) -> None:
    assert array_equal(around(frame_cp.get_vector_a(), decimals=2), [-1.0, 0.0, -1.41])


def test_cp_vector_g(frame_cp: CrossProductMethod) -> None:
    assert array_equal(around(frame_cp.get_vector_g(), decimals=2), [-1.0, 0.0, 1.41])


def test_rm_vector_a(frame_rm: RodriguesMethod) -> None:
    assert array_equal(around(frame_rm.get_vector_a(), decimals=1), [-0.5, 0.0, -0.5])


def test_rm_vector_g(frame_rm: RodriguesMethod) -> None:
    assert array_equal(around(frame_rm.get_vector_g(), decimals=1), [-0.5, 0.0, 0.5])
