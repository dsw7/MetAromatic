from os import path
from pytest import fixture

@fixture
def default_met_aromatic_parameters(scope='session'):
    return {
        'distance': 4.9,
        'angle': 109.5,
        'chain': 'A',
        'model': 'cp',
    }
