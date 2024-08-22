from dataclasses import dataclass
from json import loads
from pathlib import Path
import pytest
from MetAromatic import get_bridges
from MetAromatic.models import MetAromaticParams, BridgeSpace

NETWORK_SIZE = 4
NUM_BRIDGES = 100
PARAMS = MetAromaticParams(
    cutoff_distance=6.0,
    cutoff_angle=360.0,
    chain="A",
    model="cp",
)
PATH_TEST_DATA = (
    Path(__file__).resolve().parent / "data_n_3_bridges_no_ang_limit_6_angstroms.json"
)

if not PATH_TEST_DATA.exists():
    pytest.exit(f"File {PATH_TEST_DATA} is missing")


@dataclass
class ControlBridge:
    bridge: list[str]
    pdb_code: str


def get_control_bridges() -> list[ControlBridge]:
    with PATH_TEST_DATA.open() as f:
        data = [loads(line) for line in f]

    bridges = []

    for datum in data[0:NUM_BRIDGES]:
        bridges.append(ControlBridge(pdb_code=datum["code"], bridge=datum["bridge"]))

    return bridges


def get_control_bridge_test_ids() -> list[str]:
    with PATH_TEST_DATA.open() as f:
        data = [loads(line) for line in f]

    pdb_codes = []
    for datum in data[0:NUM_BRIDGES]:
        pdb_codes.append(datum.get("code").lower())

    return pdb_codes


@pytest.mark.parametrize(
    "bridge", get_control_bridges(), ids=get_control_bridge_test_ids()
)
def test_bridge_benchmark(bridge: ControlBridge) -> None:
    try:
        bs: BridgeSpace = get_bridges(
            code=bridge.pdb_code, params=PARAMS, vertices=NETWORK_SIZE
        )
    except IndexError:
        pytest.skip(
            "Skipping list index out of range error. Occurs because of missing data."
        )
    else:
        assert set(bridge.bridge) in bs.bridges
