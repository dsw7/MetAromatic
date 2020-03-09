from json import loads
from os import path
from pytest import mark, skip, exit
from .met_aromatic import MetAromatic
from .utilities import errors


CONTROL_BRIDGE_DATA = path.join(
    path.dirname(path.abspath(__file__)),
    './test_data/test_n_3_bridges_no_ang_limit_6_angstroms.json'
)


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
def test_bridge_collector(bridges, default_bridge_testing_parameters):
    try:
        bridging_interactions = MetAromatic(
            code=bridges.get('pdb_code'),
            cutoff_angle=default_bridge_testing_parameters['angle'],
            cutoff_distance=default_bridge_testing_parameters['distance'],
            model=default_bridge_testing_parameters['model'],
            chain=default_bridge_testing_parameters['chain']
        ).get_bridging_interactions(
            number_vertices=default_bridge_testing_parameters['network_size']
        )
    except IndexError:
        skip('Skipping list index out of range error. Occurs because of missing data.')
    else:
        assert set(bridges.get('bridge')) in bridging_interactions


@mark.parametrize(
    'code, cutoff_distance, cutoff_angle, error',
    [
        ('1rcy', 0.00, 109.5, errors.ErrorCodes.InvalidCutoffsError),
        ('1rcy', 4.95, 720.0, errors.ErrorCodes.InvalidCutoffsError),
        ('2rcy', 4.95, 109.5, errors.ErrorCodes.NoMetCoordinatesError),
        ('3nir', 4.95, 109.5, errors.ErrorCodes.NoMetCoordinatesError),
        ('abcd', 4.95, 109.5, errors.ErrorCodes.InvalidPDBFileError)
    ],
    ids=[
        "Testing errors.ErrorCodes.InvalidCutoffsError",
        "Testing errors.ErrorCodes.InvalidCutoffsError",
        "Testing errors.ErrorCodes.NoMetCoordinatesError",
        "Testing errors.ErrorCodes.NoMetCoordinatesError",
        "Testing errors.ErrorCodes.InvalidPDBFileError"
    ]
)
def test_no_bridges_response(code, cutoff_distance, cutoff_angle, default_bridge_testing_parameters, error):
    assert MetAromatic(
        code=code,
        cutoff_angle=cutoff_angle,
        cutoff_distance=cutoff_distance,
        model=default_bridge_testing_parameters['model'],
        chain=default_bridge_testing_parameters['chain']
    ).get_bridging_interactions(
        number_vertices=default_bridge_testing_parameters['network_size']
    ) == error
