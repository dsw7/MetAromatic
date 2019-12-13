import sys
from sys import path; path.append('../metaromatic')
from csv import reader
from random import sample
from json import loads
from versionhandler import VersionHandler


def pytest_report_header(config):
    version = VersionHandler('..').get_version().get('__version__')
    return 'Testing MetAromatic v. {}'.format(version)


class Setup:
    protein_identities = [
        {'pdb_code': '3lta', 'description': 'ATP BINDING PROTEIN-DX'},
        {'pdb_code': '5exn', 'description': 'COAGULATION FACTOR XIA LIGHT CHAIN'},
        {'pdb_code': '3a42', 'description': 'FORMAMIDOPYRIMIDINE-DNA GLYCOSYLASE'},
        {'pdb_code': '2aqt', 'description': 'SUPEROXIDE DISMUTASE [CU-ZN]'},
        {'pdb_code': '5l4v', 'description': 'PROTEIN FIMH'},
        {'pdb_code': '6b29', 'description': 'SH3 AND CYSTEINE-RICH DOMAIN-CONTAINING PROTEIN 3'},
        {'pdb_code': '4c0h', 'description': 'MRNA CLEAVAGE AND POLYADENYLATION FACTOR CLP1'},
        {'pdb_code': '5t6j', 'description': 'KINETOCHORE PROTEIN SPC24'}
    ]

    protein_organisms = [
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

    def get_control_ec_codes(file):
        try:
            data = []
            with open(file) as csvfile:
                for row in reader(csvfile, delimiter=','):
                    data.append({'pdb_code': row[0], 'ec_code': row[1]})
        except FileNotFoundError:
            sys.exit('File {} is missing.'.format(file))
        else:
            return data

    def get_control_bridges(file, size=100):
        try:
            with open(file, 'r') as jsonfile:
                data = [loads(line) for line in jsonfile]
        except FileNotFoundError:
            sys.exit('File {} is missing.'.format(file))
        else:
            outgoing = []
            for datum in sample(data, size):
                outgoing.append({'pdb_code': datum.get('code'), 'bridge': datum.get('bridge')})
            return outgoing
