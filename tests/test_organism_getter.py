from sys import path; path.append('../metaromatic')
from pytest import mark
from ma3 import MetAromatic


PROTEIN_ORGANISMS = [
    {'pdb_code': '3lta', 'organism': 'SYNTHETIC CONSTRUCT'},
    {'pdb_code': '5exn', 'organism': 'HOMO SAPIENS'},
    {'pdb_code': '3a42', 'organism': 'ACANTHAMOEBA POLYPHAGA MIMIVIRUS'},
    {'pdb_code': '2aqt', 'organism': 'NEISSERIA MENINGITIDIS'},
    {'pdb_code': '5l4v', 'organism': 'ESCHERICHIA COLI (STRAIN K12)'},
    {'pdb_code': '6b29', 'organism': 'HOMO SAPIENS'},
    {'pdb_code': '4c0h', 'organism': 'SACCHAROMYCES CEREVISIAE'},
    {'pdb_code': '5t6j', 'organism': 'SACCHAROMYCES CEREVISIAE (STRAIN ATCC 204508 /  '},
    {'pdb_code': '1rcy', 'organism': 'ACIDITHIOBACILLUS FERROOXIDANS'},
    {'pdb_code': '4bph', 'organism': 'BACILLUS SUBTILIS'},
    {'pdb_code': '1erh', 'organism': 'HOMO SAPIENS'},
    {'pdb_code': '1xor', 'organism': 'HOMO SAPIENS'},
    {'pdb_code': '2rcy', 'organism': 'PLASMODIUM FALCIPARUM'},
    {'pdb_code': '1ucy', 'organism': 'BOS TAURUS'}
]


@mark.parametrize(
    'organism_data',
    PROTEIN_ORGANISMS,
    ids=[i.get('pdb_code') for i in PROTEIN_ORGANISMS]
)
def test_metaromatic_algorithm_organism_getter(organism_data):
    assert MetAromatic(organism_data.get('pdb_code')).get_organism() == organism_data.get('organism')
