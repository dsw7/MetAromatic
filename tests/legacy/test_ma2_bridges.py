"""
dsw7@sfu.ca

Testing the MetAromatic bridging interaction algorithm.

dataset: We are using low redundancy structures here
dataset: 3-bridges
dataset: Cutoff distace is 6 angstroms
dataset: Cutoff angle is inf
"""

from json import loads
from random import sample
from sys import path
path.append('..')
import pytest
from ma2 import MetAromatic

CUTOFF = 6.0
ANGLE = 360.00
TEST_DATA = 'test_n_3_bridges_no_ang_limit_6_angstroms.json'

def get_control_bridges(filename, number=100):
    """ Get 3-bridges from previously collected dataset """
    data, outgoing = [], []
    with open(filename, 'r') as file:
        for line in file:
            data.append(loads(line))
    for datum in sample(data, number):
        outgoing.append((datum.get('code'), datum.get('bridge')))
    return outgoing

def get_test_bridges(code):
    obj = MetAromatic(code=code, angle=ANGLE, cutoff=CUTOFF)
    obj.met_aromatic()
    # have to use n + 1 to include met
    # have to use in clause because ma returns
    # multiple bridges (including inverts)
    return obj.bridging_interactions(n=4)

@pytest.mark.parametrize('code, bridge', get_control_bridges(TEST_DATA))
def test_eval(code, bridge):
    """ Check that algorithm returns 3-bridges identical to control """
    bridges = get_test_bridges(code)
    assert set(bridge) in bridges
