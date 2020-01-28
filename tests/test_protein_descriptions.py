from sys import path; path.append('../metaromatic')
from pytest import mark
from ma3 import MetAromatic
CONTROL_EC_CODES = './controls/test_dataset_ec_codes.csv'


PROTEIN_IDENTITIES = [
    {'pdb_code': '3lta', 'description': 'ATP BINDING PROTEIN-DX'},
    {'pdb_code': '5exn', 'description': 'COAGULATION FACTOR XIA LIGHT CHAIN'},
    {'pdb_code': '3a42', 'description': 'FORMAMIDOPYRIMIDINE-DNA GLYCOSYLASE'},
    {'pdb_code': '2aqt', 'description': 'SUPEROXIDE DISMUTASE [CU-ZN]'},
    {'pdb_code': '5l4v', 'description': 'PROTEIN FIMH'},
    {'pdb_code': '6b29', 'description': 'SH3 AND CYSTEINE-RICH DOMAIN-CONTAINING PROTEIN 3'},
    {'pdb_code': '4c0h', 'description': 'MRNA CLEAVAGE AND POLYADENYLATION FACTOR CLP1'},
    {'pdb_code': '5t6j', 'description': 'KINETOCHORE PROTEIN SPC24'}
]


@mark.parametrize(
    'identities',
    PROTEIN_IDENTITIES,
    ids=[i.get('pdb_code') for i in PROTEIN_IDENTITIES]
)
def test_protein_identities(identities):
    assert MetAromatic(identities.get('pdb_code')).get_protein_identity() == identities.get('description')
