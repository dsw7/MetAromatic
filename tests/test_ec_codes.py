from sys import path; path.append('../metaromatic')
from csv import reader
from pytest import mark, exit
from ma3 import MetAromatic
CONTROL_EC_CODES = './controls/test_dataset_ec_codes.csv'


def get_control_ec_codes(file):
    try:
        ec_codes = []
        with open(file) as csvfile:
            for row in reader(csvfile, delimiter=','):
                ec_codes.append({'pdb_code': row[0], 'ec_code': row[1]})
    except FileNotFoundError:
        exit(f'File {file} is missing.')
    else:
        return ec_codes


def get_test_ids(file):
    try:
        with open(file) as csvfile:
            ids = [row[0] for row in reader(csvfile, delimiter=',')]
    except FileNotFoundError:
        exit(f'File {file} is missing.')
    else:
        return ids


@mark.parametrize(
    'ec_code',
    get_control_ec_codes(CONTROL_EC_CODES),
    ids=get_test_ids(CONTROL_EC_CODES)
)
def test_ec_codes(ec_code):
    control_ec_code = ec_code.get('ec_code')
    test_ec_code = MetAromatic(ec_code.get('pdb_code')).get_ec_classifier()
    if control_ec_code == '':
        assert not test_ec_code
    else:
        assert test_ec_code == control_ec_code
