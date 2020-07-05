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

@fixture
def default_bridge_testing_parameters(scope='session'):
    return {
        'distance': 6.0,
        'angle': 360.0,
        'chain': 'A',
        'model': 'cp',
        'network_size': 4
    }

@fixture
def get_483_control_data(scope='session'):
    root = path.dirname(path.abspath(__file__))
    path_to_file = path.join(root, './test_data/test_483OutputA3-3-M-Benchmark.csv')
    data = []
    for line in open(path_to_file):
        data.append(line.strip('\n').split(','))
    return data
