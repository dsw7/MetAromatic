from json import loads
from pathlib import Path
import pytest
from .bridge import GetBridgingInteractions

NETWORK_SIZE = 4
NUM_BRIDGES = 100

TEST_PARAMETERS = {
    'cutoff_distance': 6.0,
    'cutoff_angle': 360.0,
    'chain': 'A',
    'model': 'cp'
}

PATH_TEST_DATA = Path(__file__).resolve().parent / 'test_data' / 'data_n_3_bridges_no_ang_limit_6_angstroms.json'

if not PATH_TEST_DATA.exists():
    pytest.exit(f'File {PATH_TEST_DATA} is missing')

def get_control_bridges():

    with PATH_TEST_DATA.open() as f:
        data = [loads(line) for line in f]

    bridges = []

    for datum in data[0:NUM_BRIDGES]:
        bridges.append({
            'pdb_code': datum.get('code'),
            'bridge': datum.get('bridge')
        })

    return bridges

def get_control_bridge_test_ids():

    with PATH_TEST_DATA.open() as f:
        data = [loads(line) for line in f]

    pdb_codes = []
    for datum in data[0:NUM_BRIDGES]:
        pdb_codes.append(datum.get('code').lower())

    return pdb_codes

@pytest.mark.test_command_line_interface
@pytest.mark.parametrize('bridges', get_control_bridges(), ids=get_control_bridge_test_ids())
def test_bridge_collector(bridges):

    try:
        handle = GetBridgingInteractions(TEST_PARAMETERS)
        handle.get_bridging_interactions(vertices=NETWORK_SIZE, code=bridges.get('pdb_code'))
    except IndexError:
        pytest.skip('Skipping list index out of range error. Occurs because of missing data.')
    else:
        assert set(bridges.get('bridge')) in handle.bridges

@pytest.mark.test_command_line_interface
@pytest.mark.parametrize(
    'code, cutoff_distance, cutoff_angle',
    [
        ('1rcy', 0.00, 109.5),
        ('1rcy', 4.95, 720.0),
        ('2rcy', 4.95, 109.5),
        ('3nir', 4.95, 109.5),
        ('abcd', 4.95, 109.5)
    ],
    ids=[
        "Testing InvalidCutoffsError",
        "Testing InvalidCutoffsError",
        "Testing NoMetCoordinatesError",
        "Testing NoMetCoordinatesError",
        "Testing InvalidPDBFileError"
    ]
)
def test_no_bridges_response(code, cutoff_distance, cutoff_angle):

    params = {
        'cutoff_angle': cutoff_angle,
        'cutoff_distance': cutoff_distance,
        'model': TEST_PARAMETERS['model'],
        'chain': TEST_PARAMETERS['chain']
    }

    handle = GetBridgingInteractions(params)
    handle.get_bridging_interactions(code=code, vertices=NETWORK_SIZE)

    assert len(handle.bridges) == 0
