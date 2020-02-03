from sys import path; path.append('../src')
from json import loads
from pytest import mark, skip, exit
from met_aromatic import MetAromatic
from utilities import errors


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
            outgoing.append({
                'pdb_code': datum.get('code'),
                'bridge': datum.get('bridge')
            })
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
        bridging_interactions = MetAromatic(
            code=bridges.get('pdb_code'),
            cutoff_angle=ANGLE_BRIDGE_TESTS,
            cutoff_distance=CUTOFF_BRIDGE_TESTS
        ).get_bridging_interactions(number_vertices=SIZE_NETWORK)
    except IndexError:
        skip('Skipping list index out of range error. Occurs because of missing data.')
    else:
        assert set(bridges.get('bridge')) in bridging_interactions


@mark.parametrize(
    'code, cutoff_distance, cutoff_angle',
    [
        ('1rcy', 0.00, 109.5),
        ('1rcy', 4.95, 720.0),
        ('2rcy', 4.95, 109.5),
        ('3nir', 4.95, 109.5),
        ('abcd', 4.95, 109.5)
    ],
    ids=[
        "Testing errors.InvalidCutoffsError",
        "Testing errors.InvalidCutoffsError",
        "Testing errors.NoMetCoordinatesError",
        "Testing errors.NoMetCoordinatesError",
        "Testing errors.InvalidPDBFileError"
    ]
)
def test_no_bridges_response(code, cutoff_distance, cutoff_angle):
    assert issubclass(
        MetAromatic(
            code=code,
            cutoff_angle=cutoff_angle,
            cutoff_distance=cutoff_distance
        ).get_bridging_interactions(number_vertices=SIZE_NETWORK), errors.Error)
