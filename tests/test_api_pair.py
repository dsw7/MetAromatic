from pytest import mark
from MetAromatic.pair import MetAromatic

TEST_PARAMETERS = {
    'cutoff_distance': 4.9,
    'cutoff_angle': 109.5,
    'chain': 'A',
    'model': 'cp'
}

VALID_RESULTS_1RCY = [
    {
        'aromatic_residue': 'TYR', 'aromatic_position': '122', 'methionine_position': '18',
        'norm': 4.211, 'met_theta_angle': 75.766, 'met_phi_angle': 64.317
    },
    {
        'aromatic_residue': 'TYR', 'aromatic_position': '122', 'methionine_position': '18',
        'norm': 3.954, 'met_theta_angle': 60.145, 'met_phi_angle': 68.352
    },
    {
        'aromatic_residue': 'TYR', 'aromatic_position': '122', 'methionine_position': '18',
        'norm': 4.051, 'met_theta_angle': 47.198, 'met_phi_angle': 85.151
    },
    {
        'aromatic_residue': 'TYR', 'aromatic_position': '122', 'methionine_position': '18',
        'norm': 4.39, 'met_theta_angle': 53.4, 'met_phi_angle': 95.487
    },
    {
        'aromatic_residue': 'TYR', 'aromatic_position': '122', 'methionine_position': '18',
        'norm': 4.62, 'met_theta_angle': 68.452, 'met_phi_angle': 90.771
    },
    {
        'aromatic_residue': 'TYR', 'aromatic_position': '122', 'methionine_position': '18',
        'norm': 4.537, 'met_theta_angle': 78.568, 'met_phi_angle': 76.406
    },
    {
        'aromatic_residue': 'PHE', 'aromatic_position': '54', 'methionine_position': '148',
        'norm': 4.777, 'met_theta_angle': 105.947, 'met_phi_angle': 143.022
    },
    {
        'aromatic_residue': 'PHE', 'aromatic_position': '54', 'methionine_position': '148',
        'norm': 4.61, 'met_theta_angle': 93.382, 'met_phi_angle': 156.922
    },
    {
        'aromatic_residue': 'PHE', 'aromatic_position': '54', 'methionine_position': '148',
        'norm': 4.756, 'met_theta_angle': 93.287, 'met_phi_angle': 154.63
    }
]

def test_pair_1rcy_valid_results():

    sum_met_theta_control = sum(i['met_theta_angle'] for i in VALID_RESULTS_1RCY)
    sum_met_phi_control = sum(i['met_phi_angle'] for i in VALID_RESULTS_1RCY)

    results = MetAromatic(**TEST_PARAMETERS).get_met_aromatic_interactions(code='1rcy')

    sum_met_theta_test = sum(i['met_theta_angle'] for i in results.interactions)
    sum_met_phi_test = sum(i['met_phi_angle'] for i in results.interactions)

    assert sum_met_theta_control == sum_met_theta_test
    assert sum_met_phi_control == sum_met_phi_test

@mark.parametrize(
    'code, cutoff_distance, cutoff_angle, model, status',
    [
        ('1rcy', -0.01,  109.5,  'cp', 'Invalid cutoff distance'),
        ('1rcy',  4.95,  -60.0,  'cp', 'Invalid cutoff angle'),
        ('1rcy',  4.95,  720.0,  'cp', 'Invalid cutoff angle'),
        ('2rcy',  4.95,  109.5,  'cp', 'No MET residues'),
        ('3nir',  4.95,  109.5,  'cp', 'No MET residues'),
        ('abcd',  4.95,  109.5,  'cp', 'Invalid PDB entry'),
        ('1rcy',  4.95,  109.5,  'pc', 'Invalid model'),
        ('1rcy', '4.95', 109.5,  'cp', 'Cutoff distance must be a valid float'),
        ('1rcy',  4.95, '109.5', 'cp', 'Cutoff angle must be a valid float'),
        ('1rcy',  4.95,  109.5,    25, 'Model must be a valid string')
    ]
)
def test_pair_invalid_inputs(code, cutoff_distance, cutoff_angle, model, status):

    results = MetAromatic(
        cutoff_angle=cutoff_angle,
        cutoff_distance=cutoff_distance,
        chain='A',
        model=model
    ).get_met_aromatic_interactions(code=code)

    assert not results.OK
    assert results.status == status

def test_pair_no_results_error():
    results = MetAromatic(**TEST_PARAMETERS).get_met_aromatic_interactions(code='1a5r')

    assert results.status == 'No interactions'
    assert results.OK
