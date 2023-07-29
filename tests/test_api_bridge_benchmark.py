from json import loads
from pathlib import Path
from pytest import mark, exit, skip
from MetAromatic import GetBridgingInteractions

NETWORK_SIZE = 4
NUM_BRIDGES = 100

TEST_PARAMETERS = {
    'cutoff_distance': 6.0,
    'cutoff_angle': 360.0,
    'chain': 'A',
    'model': 'cp'
}

PATH_TEST_DATA = Path(__file__).resolve().parent / 'data_n_3_bridges_no_ang_limit_6_angstroms.json'

if not PATH_TEST_DATA.exists():
    exit(f'File {PATH_TEST_DATA} is missing')

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

@mark.parametrize('bridges', get_control_bridges(), ids=get_control_bridge_test_ids())
def test_bridge_benchmark(bridges):

    try:
        results = GetBridgingInteractions(
            TEST_PARAMETERS
        ).get_bridging_interactions(
            vertices=NETWORK_SIZE, code=bridges.get('pdb_code')
        )
    except IndexError:
        skip('Skipping list index out of range error. Occurs because of missing data.')
    else:
        assert set(bridges.get('bridge')) in results['bridges']
