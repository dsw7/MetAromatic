from typing import TypeAlias, TypedDict
from json import loads
from pathlib import Path
import pytest
from utils import Defaults
from MetAromatic import get_bridges
from MetAromatic.models import BridgeSpace


class DefaultsBridge(Defaults):
    vertices: int


class BridgeData(TypedDict):
    EC: str
    bridges: list[list[str]]


ControlData: TypeAlias = dict[str, BridgeData]


@pytest.fixture(scope="module")
def search_params() -> DefaultsBridge:
    """
    Parameters used to generate the data_n_3_bridges_no_ang_limit_6_angstroms.json
    control data file.
    """
    return DefaultsBridge(
        chain="A",
        cutoff_angle=360.0,
        cutoff_distance=6.0,
        model="cp",
        vertices=4,  # I.e. n = 3 bridges
    )


@pytest.fixture(scope="module")
def known_bridges(resources: Path) -> ControlData:
    raw_data: str = (
        resources / "data_n_3_bridges_no_ang_limit_6_angstroms.json"
    ).read_text()

    data: ControlData = loads(raw_data)
    return data


TEST_CODES = [
    "2HM7",
    "2ORT",
    "4GXW",
    "4YU6",
    "4CAG",
    "4PM4",
    "5L20",
    "4GFT",
    "5UL8",
    "6DCH",
    "4YN5",
    "1BJJ",
    "4CE5",
    "3TC5",
    "2E5W",
    "2YJG",
    "5HK1",
    "5WX1",
    "2B71",
    "1YE9",
    "5U69",
    "3DKP",
    "2B7U",
    "6F3P",
    "4UPK",
    "6EUA",
    "3QFE",
    "2XHY",
    "5Z2C",
    "1GWI",
    "1RQG",
    "6IBX",
    "3D59",
    "4L8F",
    "5OUP",
    "3CN5",
    "5UN8",
    "1BUN",
    "1JAL",
    "5K5S",
    "2PQ6",
    "4X6X",
    "3MJO",
    "6GH3",
    "1C8Z",
    "3AKH",
    "6FBM",
    "2CKG",
    "5C1M",
    "3OF7",
    "6BNI",
    "5TEC",
    "6HNS",
    "6GMC",
    "2QK4",
    "3ALU",
    "5I9J",
    "1MHQ",
    "4J78",
    "3PE6",
    "2Z1D",
    "5V2J",
    "4W8K",
    "5OC1",
    "5N9X",
    "5N6F",
    "6EOF",
    "2C53",
    "5UA4",
    "5C98",
    "5MED",
    "4ZZP",
    "4ZZQ",
    "3TO5",
    "1L2H",
    "3G5C",
    "2EXH",
    "5CER",
    "3N90",
    "5HVN",
    "5DBJ",
    "3D9D",
    "5MSE",
    "2AXQ",
    "2F1V",
    "1KEA",
    "4FAI",
    "3GRH",
    "1WST",
    "3TW5",
    "3ZOJ",
    "2X24",
    "1XM8",
    "2I1S",
    "5G5O",
    "4WXP",
    "5OWU",
    "4WY8",
    "2PK2",
    "1GUX",
]


@pytest.mark.parametrize("pdb_code", TEST_CODES)
def test_bridge_benchmark(
    pdb_code: str, known_bridges: ControlData, search_params: DefaultsBridge
) -> None:
    try:
        bs: BridgeSpace = get_bridges(code=pdb_code, **search_params)
    except IndexError:
        pytest.skip(
            "Skipping list index out of range error. Occurs because of missing data."
        )

    for bridge in known_bridges[pdb_code]["bridges"]:
        assert set(bridge) in bs.bridges
