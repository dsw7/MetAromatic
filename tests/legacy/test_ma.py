"""
dsw7@sfu.ca

Testing the MetAromatic algorithm against a very old routine I wrote years ago.
"""

from sys import path
path.append('..')
import pytest
from pandas import DataFrame, read_csv, testing
from ma import MetAromatic


CUTOFF = 4.9
ANGLE = 109.5
CHAIN = 'A'
COLUMNS = ['ARO', 'ARO RES', 'MET', 'MET RES', 'NORM', 'MET-THETA', 'MET-PHI']
NAMES_CSV = ['ARO', 'ARO RES', 'MET', 'MET RES', 'MET-PHI', 'MET-THETA', 'NORM', 'PDBCODE']
CONTROL = read_csv('./test_483OutputA3-3-M-Benchmark.csv', names=NAMES_CSV)
CODES_TEST = set(CONTROL.PDBCODE)


def get_control_dataset(code):
    """ Get data from MA-2-483 algorithm written years ago """
    df_control = CONTROL[CONTROL.PDBCODE == code]
    df_control = df_control.drop(['PDBCODE'], axis=1)
    df_control = df_control.reindex(sorted(df_control.columns), axis=1)
    df_control = df_control.sort_values(by='NORM')
    df_control = df_control.reset_index(drop=True)
    return df_control


def get_test_dataset(code):
    """ Get data from current Met-aromatic algorithm """
    obj_ma = MetAromatic(code, chain=CHAIN, cutoff=CUTOFF, angle=ANGLE, model='cp').met_aromatic()
    df_test = DataFrame(obj_ma, columns=COLUMNS)
    df_test = df_test.reindex(sorted(df_test.columns), axis=1)
    df_test = df_test.sort_values(by='NORM')
    df_test = df_test.reset_index(drop=True)
    df_test = df_test.astype({'MET RES': 'int64', 'ARO RES': 'int64'})
    return df_test


@pytest.mark.parametrize("code", CODES_TEST)
def test_eval(code):
    """ Test that output from both control and test is identical """
    df_control = get_control_dataset(code=code)
    df_test = get_test_dataset(code=code)
    testing.assert_frame_equal(df_control, df_test)
