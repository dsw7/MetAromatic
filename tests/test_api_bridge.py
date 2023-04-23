from pytest import mark
from MetAromatic.bridge import GetBridgingInteractions

NETWORK_SIZE = 4
TEST_PARAMETERS = {
    'cutoff_distance': 6.0,
    'cutoff_angle': 360.0,
    'chain': 'A',
    'model': 'cp'
}

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

    results = GetBridgingInteractions(params).get_bridging_interactions(code=code, vertices=NETWORK_SIZE)
    assert len(results.bridges) == 0
