from json import loads
from typing import Optional
from os import path
from pytest import (
    mark,
    skip,
    exit
)
from .helpers.consts import EXIT_FAILURE
from .bridge import GetBridgingInteractions

CONTROL_BRIDGE_DATA = path.join(
    path.dirname(path.abspath(__file__)), 'helpers', 'data_n_3_bridges_no_ang_limit_6_angstroms.json'
)
NETWORK_SIZE = 4
TEST_PARAMETERS = {
    'cutoff_distance': 6.0,
    'cutoff_angle': 360.0,
    'chain': 'A',
    'model': 'cp'
}

def get_control_bridges(file: str, size: Optional[int] = 100) -> list:
    try:
        with open(file, 'r') as jsonfile:
            data = [loads(line) for line in jsonfile]
    except FileNotFoundError:
        exit('File {} is missing.'.format(file))

    outgoing = []
    for datum in data[0:size]:
        outgoing.append({
            'pdb_code': datum.get('code'),
            'bridge': datum.get('bridge')
        })
    return outgoing

def get_control_bridge_test_ids(file: str, size: Optional[int] = 100) -> list:
    try:
        with open(file, 'r') as jsonfile:
            data = [loads(line) for line in jsonfile]
    except FileNotFoundError:
        exit('File {} is missing.'.format(file))

    outgoing = []
    for datum in data[0:size]:
        outgoing.append(datum.get('code').lower())
    return outgoing

@mark.test_command_line_interface
@mark.parametrize(
    'bridges',
    get_control_bridges(CONTROL_BRIDGE_DATA),
    ids=get_control_bridge_test_ids(CONTROL_BRIDGE_DATA)
)
def test_bridge_collector(bridges: list) -> None:
    try:
        bridging_interactions = GetBridgingInteractions(**TEST_PARAMETERS).get_bridging_interactions(
            vertices=NETWORK_SIZE, code=bridges.get('pdb_code')
        )
    except IndexError:
        skip('Skipping list index out of range error. Occurs because of missing data.')
    else:
        assert set(bridges.get('bridge')) in bridging_interactions['results']

@mark.test_command_line_interface
@mark.parametrize(
    'code, cutoff_distance, cutoff_angle, error',
    [
        ('1rcy', 0.00, 109.5, EXIT_FAILURE),
        ('1rcy', 4.95, 720.0, EXIT_FAILURE),
        ('2rcy', 4.95, 109.5, EXIT_FAILURE),
        ('3nir', 4.95, 109.5, EXIT_FAILURE),
        ('abcd', 4.95, 109.5, EXIT_FAILURE)
    ],
    ids=[
        "Testing InvalidCutoffsError",
        "Testing InvalidCutoffsError",
        "Testing NoMetCoordinatesError",
        "Testing NoMetCoordinatesError",
        "Testing InvalidPDBFileError"
    ]
)
def test_no_bridges_response(code: str, cutoff_distance: float, cutoff_angle: float, error: int) -> None:
    assert GetBridgingInteractions(
        cutoff_angle=cutoff_angle,
        cutoff_distance=cutoff_distance,
        model=TEST_PARAMETERS['model'],
        chain=TEST_PARAMETERS['chain']
    ).get_bridging_interactions(
        code=code, vertices=NETWORK_SIZE
    )['exit_code'] == error
