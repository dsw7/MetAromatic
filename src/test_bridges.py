from json import loads
from os import path
from pytest import mark, skip, exit
from .met_aromatic import MetAromatic
from .consts import EXIT_FAILURE

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

    outgoing = []
    for datum in data[0:size]:
        outgoing.append(datum.get('code').lower())
    return outgoing


class TestBridges:
    def setup_class(self):
        self.network_size = 4
        self.default_bridge_testing_parameters = {
            'cutoff_distance': 6.0,
            'cutoff_angle': 360.0,
            'chain': 'A',
            'model': 'cp'
        }
        self.ma = MetAromatic(**self.default_bridge_testing_parameters)

    @mark.parametrize(
        'bridges',
        get_control_bridges(CONTROL_BRIDGE_DATA),
        ids=get_control_bridge_test_ids(CONTROL_BRIDGE_DATA)
    )
    def test_bridge_collector(self, bridges):
        try:
            bridging_interactions = self.ma.get_bridging_interactions(
                number_vertices=self.network_size,
                code=bridges.get('pdb_code')
            )
        except IndexError:
            skip('Skipping list index out of range error. Occurs because of missing data.')
        else:
            assert set(bridges.get('bridge')) in bridging_interactions['results']

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
    def test_no_bridges_response(self, code, cutoff_distance, cutoff_angle, error):
        assert MetAromatic(
            cutoff_angle=cutoff_angle,
            cutoff_distance=cutoff_distance,
            model=self.default_bridge_testing_parameters['model'],
            chain=self.default_bridge_testing_parameters['chain']
        ).get_bridging_interactions(
            code=code, number_vertices=self.network_size
        )['exit_code'] == error
