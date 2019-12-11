"""
dsw7@sfu.ca

Testing the MetAromatic bridging interaction algorithm.

dataset: We are using low redundancy structures here
dataset: 3-bridges
dataset: Cutoff distace is 6 angstroms
dataset: Cutoff angle is inf
"""

from sys import path
from csv import reader
path.append('..')
import pytest
from ma2 import MetAromatic

TEST_DATA = 'test_dataset_ec_codes.csv'

with open(TEST_DATA) as csvfile:
    data = reader(csvfile, delimiter=',')
    CODES_EC = [d[0:2] for d in data]
    IDS = [d[0] for d in CODES_EC]

def get_ec_classifier(code):
    return MetAromatic(code=code).get_ec_classifier()

@pytest.mark.parametrize('code, control_ec_code', CODES_EC, ids=IDS)
def test_ec_code_getter(code, control_ec_code):
    test_ec_code = get_ec_classifier(code)
    if control_ec_code == '':
        assert test_ec_code is None
    else:
        assert test_ec_code == control_ec_code
