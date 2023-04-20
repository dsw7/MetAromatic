# pylint: disable=C0415   # Disable "Import outside toplevel"

import pytest

@pytest.mark.test_packaging
def test_import_pair():

    arguments = {
        'cutoff_distance': 4.9,
        'cutoff_angle': 109.5,
        'chain': 'A',
        'model': 'cp'
    }

    from MetAromatic.core.pair import MetAromatic
    assert MetAromatic(**arguments).get_met_aromatic_interactions('1rcy')['_id'] == '1rcy'

@pytest.mark.test_packaging
def test_import_bridge():
    arguments = {
        'cutoff_distance': 6.0,
        'cutoff_angle': 360.00,
        'chain': 'A',
        'model': 'cp'
    }

    from MetAromatic.core.bridge import GetBridgingInteractions
    assert GetBridgingInteractions(**arguments).get_bridging_interactions('7mdh', 4)['_id'] == '7mdh'
