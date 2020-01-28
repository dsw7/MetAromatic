from sys import path; path.append('../metaromatic')
from json import loads
from pytest import mark, skip, exit
from ma3 import MetAromatic
CONTROL_BRIDGE_DATA = './controls/test_n_3_bridges_no_ang_limit_6_angstroms.json'
ANGLE_BRIDGE_TESTS = 360.00
CUTOFF_BRIDGE_TESTS = 6.0
SIZE_NETWORK = 4


def get_control_bridges(file, size=100):
    try:
        with open(file, 'r') as jsonfile:
            data = [loads(line) for line in jsonfile]
    except FileNotFoundError:
        exit(f'File {file} is missing.')
    else:
        outgoing = []
        for datum in data[0:size]:
            outgoing.append({'pdb_code': datum.get('code'), 'bridge': datum.get('bridge')})
        return outgoing


def get_control_bridge_test_ids(file, size=100):
    try:
        with open(file, 'r') as jsonfile:
            data = [loads(line) for line in jsonfile]
    except FileNotFoundError:
        exit(f'File {file} is missing.')
    else:
        outgoing = []
        for datum in data[0:size]:
            outgoing.append(datum.get('code').lower())
        return outgoing


@mark.parametrize(
    'bridges',
    get_control_bridges(CONTROL_BRIDGE_DATA),
    ids=get_control_bridge_test_ids(CONTROL_BRIDGE_DATA)
)
def test_bridge_collector(bridges):
    try:
        obj_bridges = MetAromatic(code=bridges.get('pdb_code'), angle=ANGLE_BRIDGE_TESTS, cutoff=CUTOFF_BRIDGE_TESTS)
        obj_bridges.met_aromatic()
    except IndexError:
        skip('Skipping list index out of range error. Occurs because of missing data.')
    else:
        assert set(bridges.get('bridge')) in obj_bridges.bridging_interactions(n=SIZE_NETWORK)
