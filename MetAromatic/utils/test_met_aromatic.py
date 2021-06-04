from os import path
from pytest import mark, skip
from .met_aromatic import MetAromatic
from .primitives.consts import EXIT_FAILURE

TEST_CODES = {
    '1l5l', '5wr6', '5i6u', '1q83', '4qo4', '4blz', '4nxw', '2xdb', '2acx',
    '3h0k', '4xff', '1xd1', '2n2u', '1yrs', '1sly', '4zk0', '3ki3', '5hml',
    '1yop', '1n6j', '1mnh', '1i0s', '5fhv', '3f1n', '5khc', '5khk', '2alf',
    '3dpc', '3skv', '6hwr', '2wm1', '3u53', '3mhk', '1bml', '4cx1', '4a64',
    '4jbx', '1ghp', '2r9h', '3omo', '1ccb', '4bwm', '5l6o', '3fg4', '3w30',
    '2zj1', '1b1y', '5gwn', '5uxe', '5pyc', '5azh', '5otc', '1th2', '4ncm',
    '3lqz', '6dbp', '1b4w', '4j4r', '5u6e', '4tog', '5lvg', '4fcd', '3uwx',
    '6hyh', '3u4s', '1yoj', '3t12', '4rlr', '2ggi', '3ps0', '4uvt', '5e35',
    '2xuc', '4u8m', '2lko', '2owg', '1ww6', '1wel', '5qb2', '3lcc', '2itl',
    '5jvv', '5hk5', '2fhb', '2zyh', '3q8n', '4h7k', '4pba', '5dsk', '2awm',
    '4lwb', '5ton', '4i74', '2a0l', '3vr1', '6ezq', '4ju4', '1y4p', '3t3i',
    '2x3u', '4pja', '5i7o', '1r0k', '6cj4', '5yq0', '4kd4', '3zxp', '3t6u',
    '3ix9', '4boy', '1h58', '3icj', '3ahd', '5eou', '2vef', '2kx6', '2qmz',
    '5c71', '4pfa', '6eiq', '5frw', '2vmn', '6bcn', '5u1j', '5kqd', '4aqt',
    '4zlo', '6jxq', '4d56', '4m7m', '2c68', '6fuh', '3b4r', '2ba2', '4y7p',
    '2qy2', '2mwy', '3e25', '2qs4', '1q1z', '6f71', '1nuf', '5ih5', '5tss',
    '3ug7', '3g3q', '5req', '4dma', '4h5v'
}

VALID_RESULTS_1RCY = [
    {
        'aromatic_residue': 'TYR',
        'aromatic_position': '122',
        'methionine_position': '18',
        'norm': 4.211,
        'met_theta_angle': 75.766,
        'met_phi_angle': 64.317
    },
    {
        'aromatic_residue': 'TYR',
        'aromatic_position': '122',
        'methionine_position': '18',
        'norm': 3.954,
        'met_theta_angle': 60.145,
        'met_phi_angle': 68.352
    },
    {
        'aromatic_residue': 'TYR',
        'aromatic_position': '122',
        'methionine_position': '18',
        'norm': 4.051,
        'met_theta_angle': 47.198,
        'met_phi_angle': 85.151
    },
    {
        'aromatic_residue': 'TYR',
        'aromatic_position': '122',
        'methionine_position': '18',
        'norm': 4.39,
        'met_theta_angle': 53.4,
        'met_phi_angle': 95.487
    },
    {
        'aromatic_residue': 'TYR',
        'aromatic_position': '122',
        'methionine_position': '18',
        'norm': 4.62,
        'met_theta_angle': 68.452,
        'met_phi_angle': 90.771
    },
    {
        'aromatic_residue': 'TYR',
        'aromatic_position': '122',
        'methionine_position': '18',
        'norm': 4.537,
        'met_theta_angle': 78.568,
        'met_phi_angle': 76.406
    },
    {
        'aromatic_residue': 'PHE',
        'aromatic_position': '54',
        'methionine_position': '148',
        'norm': 4.777,
        'met_theta_angle': 105.947,
        'met_phi_angle': 143.022
    },
    {
        'aromatic_residue': 'PHE',
        'aromatic_position': '54',
        'methionine_position': '148',
        'norm': 4.61,
        'met_theta_angle': 93.382,
        'met_phi_angle': 156.922
    },
    {
        'aromatic_residue': 'PHE',
        'aromatic_position': '54',
        'methionine_position': '148',
        'norm': 4.756,
        'met_theta_angle': 93.287,
        'met_phi_angle': 154.63
    }
]


class TestMetAromatic:

    def setup_class(self):
        self.default_parameters = {
            'cutoff_distance': 4.9,
            'cutoff_angle': 109.5,
            'chain': 'A',
            'model': 'cp',
        }

        root = path.dirname(path.abspath(__file__))
        path_to_file = path.join(root, './test_data/test_483OutputA3-3-M-Benchmark.csv')
        self.control_data = []
        for line in open(path_to_file):
            self.control_data.append(line.strip('\n').split(','))

    @mark.parametrize(
        "code",
        TEST_CODES
    )
    def test_metaromatic_algorithm_against_483_data(self, code):
        control = []
        for row in self.control_data:
            if row[7] == code:
                control.append(row)

        try:
            test_data = MetAromatic(
                **self.default_parameters
            ).get_met_aromatic_interactions(code=code)['results']

        except IndexError:
            skip('Skipping list index out of range error. Occurs because of missing data.')

        sum_norms_control = sum([float(i[6]) for i in control])
        sum_theta_control = sum([float(i[5]) for i in control])
        sum_phi_control = sum([float(i[4]) for i in control])
        sum_norms_test = sum([float(i['norm']) for i in test_data])
        sum_theta_test = sum([float(i['met_theta_angle']) for i in test_data])
        sum_phi_test = sum([float(i['met_phi_angle']) for i in test_data])

        assert abs(sum_norms_control - sum_norms_test) < 0.01
        assert abs(sum_theta_control - sum_theta_test) < 0.01
        assert abs(sum_phi_control - sum_phi_test) < 0.01


class TestMongoDBOutput:
    def setup_class(self):
        self.default_parameters = {
            'cutoff_distance': 4.9,
            'cutoff_angle': 109.5,
            'chain': 'A',
            'model': 'cp',
        }

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
            "Testing InvalidCutoffsError - 1",
            "Testing InvalidCutoffsError - 2",
            "Testing NoMetCoordinatesError - 1",
            "Testing NoMetCoordinatesError - 2",
            "Testing InvalidPDBFileError"
        ]
    )
    def test_mongodb_output_invalid_results(self, code, cutoff_distance, cutoff_angle, error):
        assert MetAromatic(
            cutoff_angle=cutoff_angle,
            cutoff_distance=cutoff_distance,
            chain=self.default_parameters['chain'],
            model=self.default_parameters['model']
        ).get_met_aromatic_interactions(code=code)['exit_code'] == error

    @mark.parametrize(
        'code, cutoff_distance, cutoff_angle',
        [
            ('1rcy', 0.00, 109.5),
            ('1rcy', 4.95, 720.0),
            ('2rcy', 4.95, 109.5),
            ('3nir', 4.95, 109.5),
            ('abcd', 4.95, 109.5)
        ]
    )
    def test_mongodb_output_invalid_results_exception_boolean(self, code, cutoff_distance, cutoff_angle):
        assert MetAromatic(
            cutoff_angle=cutoff_angle,
            cutoff_distance=cutoff_distance,
            chain=self.default_parameters['chain'],
            model=self.default_parameters['model']
        ).get_met_aromatic_interactions(code=code).get('exit_status')

    def test_mongodb_output_valid_results(self):
        sum_met_theta_control = sum([i['met_theta_angle'] for i in VALID_RESULTS_1RCY])
        sum_met_phi_control = sum([i['met_phi_angle'] for i in VALID_RESULTS_1RCY])

        test_results = MetAromatic(
            **self.default_parameters
        ).get_met_aromatic_interactions(code='1rcy')['results']

        sum_met_theta_test = sum([i['met_theta_angle'] for i in test_results])
        sum_met_phi_test = sum([i['met_phi_angle'] for i in test_results])

        assert sum_met_theta_control == sum_met_theta_test
        assert sum_met_phi_control == sum_met_phi_test


class TestErrors:
    def setup_class(self):
        self.default_parameters = {
            'distance': 4.9,
            'angle': 109.5,
            'chain': 'A',
            'model': 'cp',
        }

    def test_invalid_distance_error(self):
        assert MetAromatic(
            cutoff_angle=self.default_parameters['angle'],
            cutoff_distance=0.00,
            model=self.default_parameters['model'],
            chain=self.default_parameters['chain']
        ).get_met_aromatic_interactions(code='1rcy')['exit_code'] == EXIT_FAILURE

    def test_invalid_angle_error(self):
        assert MetAromatic(
            cutoff_angle=-720.00,
            cutoff_distance=self.default_parameters['distance'],
            model=self.default_parameters['model'],
            chain=self.default_parameters['chain']
        ).get_met_aromatic_interactions(code='1rcy')['exit_code'] == EXIT_FAILURE

    def test_invalid_pdb_code_error(self):
        assert MetAromatic(
            cutoff_angle=self.default_parameters['angle'],
            cutoff_distance=self.default_parameters['distance'],
            model=self.default_parameters['model'],
            chain=self.default_parameters['chain']
        ).get_met_aromatic_interactions(code='foo')['exit_code'] == EXIT_FAILURE

    def test_no_met_coordinates_error(self):
        assert MetAromatic(
            cutoff_angle=self.default_parameters['angle'],
            cutoff_distance=self.default_parameters['distance'],
            model=self.default_parameters['model'],
            chain=self.default_parameters['chain']
        ).get_met_aromatic_interactions(code='3nir')['exit_code'] == EXIT_FAILURE

    def test_invalid_model_error(self):
        assert MetAromatic(
            cutoff_angle=self.default_parameters['angle'],
            cutoff_distance=self.default_parameters['distance'],
            model='foobarbaz',
            chain=self.default_parameters['chain']
        ).get_met_aromatic_interactions(code='1rcy')['exit_code'] == EXIT_FAILURE

    def test_no_results_error(self):
        assert MetAromatic(
            cutoff_angle=self.default_parameters['angle'],
            cutoff_distance=self.default_parameters['distance'],
            model=self.default_parameters['model'],
            chain=self.default_parameters['chain']
        ).get_met_aromatic_interactions(code='1a5r')['exit_code'] == EXIT_FAILURE