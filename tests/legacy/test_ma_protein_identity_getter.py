"""
dsw7@sfu.ca

Testing the protein identity fetch method.
"""

from sys import path
path.append('../metaromatic')
from ma import MetAromatic


def test_3lta():
    assert MetAromatic('3lta').get_protein_identity() == ['ATP BINDING PROTEIN-DX']

def test_5exn():
    assert MetAromatic('5exn').get_protein_identity() == ['COAGULATION FACTOR XIA LIGHT CHAIN']

def test_3a42():
    assert MetAromatic('3a42').get_protein_identity() == ['FORMAMIDOPYRIMIDINE-DNA GLYCOSYLASE']

def test_2aqt():
    assert MetAromatic('2aqt').get_protein_identity() == ['SUPEROXIDE DISMUTASE [CU-ZN]']

def test_5l4v():
    assert MetAromatic('5l4v').get_protein_identity() == ['PROTEIN FIMH']

def test_6b29():
    results = MetAromatic('6b29').get_protein_identity()
    assert results == ['SH3 AND CYSTEINE-RICH DOMAIN-CONTAINING PROTEIN 3']

def test_4c0h():
    results = MetAromatic('4c0h').get_protein_identity()
    assert results == ['MRNA CLEAVAGE AND POLYADENYLATION FACTOR CLP1', 'PCF11P']

def test_5t6j():
    results = MetAromatic('5t6j').get_protein_identity()
    assert results == ['KINETOCHORE PROTEIN SPC24',
                       'KINETOCHORE PROTEIN SPC25',
                       'KINETOCHORE-ASSOCIATED PROTEIN DSN1']
