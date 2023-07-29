from pytest import mark
from MetAromatic import GetBridgingInteractions

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
def test_bridge_invalid_inputs(code, cutoff_distance, cutoff_angle, model, status):

    params = {
        'cutoff_angle': cutoff_angle,
        'cutoff_distance': cutoff_distance,
        'model': model,
        'chain': 'A'
    }

    results = GetBridgingInteractions(params).get_bridging_interactions(code=code, vertices=4)

    assert not results.OK
    assert results.status == status

@mark.parametrize(
    'code, message',
    [
        ('1a5r', 'No Met-aromatic interactions were found'),
        ('1rcy', 'No bridges')
    ]
)
def test_no_results(code, message):

    params = {
        'cutoff_distance': 4.9,
        'cutoff_angle': 109.5,
        'chain': 'A',
        'model': 'cp'
    }

    results = GetBridgingInteractions(params).get_bridging_interactions(code=code, vertices=4)

    assert results.OK
    assert results.status == message
