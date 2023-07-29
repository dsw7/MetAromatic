from pathlib import Path
from unittest import TestCase
from pytest import mark, exit
from MetAromatic import MetAromatic, MetAromaticLocal

TEST_PARAMETERS = {
    'cutoff_distance': 4.9,
    'cutoff_angle': 109.5,
    'chain': 'A',
    'model': 'cp'
}

VALID_RESULTS_1RCY = [
    {
        'aromatic_residue': 'TYR', 'aromatic_position': 122, 'methionine_position': 18,
        'norm': 4.211, 'met_theta_angle': 75.766, 'met_phi_angle': 64.317
    },
    {
        'aromatic_residue': 'TYR', 'aromatic_position': 122, 'methionine_position': 18,
        'norm': 3.954, 'met_theta_angle': 60.145, 'met_phi_angle': 68.352
    },
    {
        'aromatic_residue': 'TYR', 'aromatic_position': 122, 'methionine_position': 18,
        'norm': 4.051, 'met_theta_angle': 47.198, 'met_phi_angle': 85.151
    },
    {
        'aromatic_residue': 'TYR', 'aromatic_position': 122, 'methionine_position': 18,
        'norm': 4.39, 'met_theta_angle': 53.4, 'met_phi_angle': 95.487
    },
    {
        'aromatic_residue': 'TYR', 'aromatic_position': 122, 'methionine_position': 18,
        'norm': 4.62, 'met_theta_angle': 68.452, 'met_phi_angle': 90.771
    },
    {
        'aromatic_residue': 'TYR', 'aromatic_position': 122, 'methionine_position': 18,
        'norm': 4.537, 'met_theta_angle': 78.568, 'met_phi_angle': 76.406
    },
    {
        'aromatic_residue': 'PHE', 'aromatic_position': 54, 'methionine_position': 148,
        'norm': 4.777, 'met_theta_angle': 105.947, 'met_phi_angle': 143.022
    },
    {
        'aromatic_residue': 'PHE', 'aromatic_position': 54, 'methionine_position': 148,
        'norm': 4.61, 'met_theta_angle': 93.382, 'met_phi_angle': 156.922
    },
    {
        'aromatic_residue': 'PHE', 'aromatic_position': 54, 'methionine_position': 148,
        'norm': 4.756, 'met_theta_angle': 93.287, 'met_phi_angle': 154.63
    }
]

def test_pair_1rcy_valid_results():
    results = MetAromatic(TEST_PARAMETERS).get_met_aromatic_interactions('1rcy')

    tc = TestCase()
    tc.maxDiff = None
    tc.assertCountEqual(results['interactions'], VALID_RESULTS_1RCY)

def test_pair_1rcy_valid_results_use_local():

    # File downloaded from RSCB PDB
    path_pdb_file = Path(__file__).resolve().parent / 'data_1rcy.pdb'

    if not path_pdb_file.exists():
        exit(f'File {path_pdb_file} is missing')

    results = MetAromaticLocal(TEST_PARAMETERS).get_met_aromatic_interactions(path_pdb_file)

    tc = TestCase()
    tc.maxDiff = None
    tc.assertCountEqual(results['interactions'], VALID_RESULTS_1RCY)

def test_pair_1rcy_valid_results_use_local_invalid_file():

    # Simulating someone passing a non-PDB formatted file into program
    path_pdb_file = Path(__file__).resolve().parent / 'data_lorem_ipsum.pdb'

    if not path_pdb_file.exists():
        exit(f'File {path_pdb_file} is missing')

    results = MetAromaticLocal(TEST_PARAMETERS).get_met_aromatic_interactions(path_pdb_file)

    assert results['status'] != 'Success'
    assert not results['OK']

@mark.parametrize(
    'code, cutoff_distance, cutoff_angle, model, status',
    [
        ('1rcy', -0.01,  109.5,  'cp', 'Invalid cutoff distance'),
        ('1rcy',  4.95,  -60.0,  'cp', 'Invalid cutoff angle'),
        ('1rcy',  4.95,  720.0,  'cp', 'Invalid cutoff angle'),
        ('2rcy',  4.95,  109.5,  'cp', 'No MET residues'),
        ('3nir',  4.95,  109.5,  'cp', 'No MET residues'),
        ('6mwm',  4.95,  109.5,  'cp', 'No PHE/TYR/TRP residues'),
        ('abcd',  4.95,  109.5,  'cp', 'Invalid PDB entry'),
        ('1rcy',  4.95,  109.5,  'pc', 'Invalid model'),
        ('1rcy', '4.95', 109.5,  'cp', 'Cutoff distance must be a valid float'),
        ('1rcy',  4.95, '109.5', 'cp', 'Cutoff angle must be a valid float'),
        ('1rcy',  4.95,  109.5,    25, 'Model must be a valid string')
    ]
)
def test_pair_invalid_inputs(code, cutoff_distance, cutoff_angle, model, status):

    params = {
        'cutoff_angle': cutoff_angle,
        'cutoff_distance': cutoff_distance,
        'chain': 'A',
        'model': model
    }

    results = MetAromatic(params).get_met_aromatic_interactions(code)
    assert not results['OK']
    assert results['status'] == status

def test_pair_no_results_error():
    results = MetAromatic(TEST_PARAMETERS).get_met_aromatic_interactions('1a5r')

    assert results['status'] == 'No interactions'
    assert results['OK']
