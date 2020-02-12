from os import path
from pytest import fixture
from pandas import read_csv


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
    return read_csv(path.join(root, './test_data/test_483OutputA3-3-M-Benchmark.csv'))


@fixture
def path_runner():
    root = path.dirname(path.dirname(path.abspath(__file__)))
    return path.join(root, 'runner.py')
