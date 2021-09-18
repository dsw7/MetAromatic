# pylint: disable=C0415   # Disable "Import outside toplevel"

from pytest import mark

@mark.test_packaging
def test_import_pair() -> None:
    arguments = {
        'cutoff_distance': 4.9,
        'cutoff_angle': 109.5,
        'chain': 'A',
        'model': 'cp'
    }

    from MetAromatic.core.pair import MetAromatic
    results = MetAromatic(**arguments).get_met_aromatic_interactions('1rcy')
    assert results['_id'] == '1rcy'

@mark.test_packaging
def test_import_bridge() -> None:
    arguments = {
        'cutoff_distance': 6.0,
        'cutoff_angle': 360.00,
        'chain': 'A',
        'model': 'cp'
    }

    from MetAromatic.core.bridge import GetBridgingInteractions
    results = GetBridgingInteractions(**arguments).get_bridging_interactions('7mdh', 4)
    assert results['_id'] == '7mdh'
