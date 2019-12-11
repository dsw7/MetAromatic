"""
dsw7@sfu.ca

Testing the MetAromatic algorithm against the version I wrote in grad school.
"""

from sys import path
path.append('..')
from random import sample
import pytest
from pandas import DataFrame, read_csv, testing
from ma import MetAromatic
from test_ma_lowlevel_from_grad_school import run_met_aromatic


CUTOFF = 4.9
ANGLE = 109.5
CHAIN = 'A'
SAMPLE_SIZE = 100
COLUMNS = ['ARO', 'ARO RES', 'MET', 'MET RES', 'NORM', 'MET-THETA', 'MET-PHI']
CODES_TEST = read_csv('./test_randomized_pdb_codes.csv', names=['PDBCODE'])
CODES_TEST = CODES_TEST.PDBCODE.tolist()[1:]
CODES_TEST = sample(CODES_TEST, SAMPLE_SIZE)


def get_control_dataset(code):
    """ Get data from grad school algorithm written years ago """
    ma_obj = run_met_aromatic(code, chain=CHAIN, cutoff=CUTOFF, angle=ANGLE, model='cp')
    df_control = DataFrame(ma_obj, columns=COLUMNS)
    df_control = df_control.reindex(sorted(df_control.columns), axis=1)
    df_control = df_control.sort_values(by='NORM')
    df_control = df_control.reset_index(drop=True)
    return df_control


def get_test_dataset(code):
    """ Get data from current Met-aromatic algorithm """
    ma_obj = MetAromatic(code, chain=CHAIN, cutoff=CUTOFF, angle=ANGLE, model='cp').met_aromatic()
    df_test = DataFrame(ma_obj, columns=COLUMNS)
    df_test = df_test.reindex(sorted(df_test.columns), axis=1)
    df_test = df_test.sort_values(by='NORM')
    df_test = df_test.reset_index(drop=True)
    return df_test


@pytest.mark.parametrize("code", CODES_TEST)
def test_eval(code):
    """ Compare test data against control data """
    df_control = get_control_dataset(code=code)
    df_test = get_test_dataset(code=code)
    testing.assert_frame_equal(df_control, df_test)


# keep this to visualize failing pdb entries
if __name__ == '__main__':
    CODE = '4qz6'
    print(get_control_dataset(CODE))
    print(get_test_dataset(CODE))
