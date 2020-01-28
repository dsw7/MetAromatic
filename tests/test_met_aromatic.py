from sys import path; path.append('../metaromatic')
from pytest import mark, skip
from pandas import DataFrame, testing, read_csv
from ma3 import MetAromatic


CONTROL_483_DATA = './controls/test_483OutputA3-3-M-Benchmark.csv'
CONTROL_483_DATA_DF = read_csv(CONTROL_483_DATA)
CUTOFF_483_TESTS = 4.9
ANGLE_483_TESTS = 109.5
COLUMNS_483_TESTS = ['ARO', 'ARO RES', 'MET', 'MET RES', 'NORM', 'MET-THETA', 'MET-PHI']


def get_ma_2_483_control_dataset_using_pandas(code):
    df_control = CONTROL_483_DATA_DF[CONTROL_483_DATA_DF.PDBCODE == code]
    df_control = df_control.drop(['PDBCODE'], axis=1)
    df_control = df_control.reindex(sorted(df_control.columns), axis=1)
    df_control = df_control.sort_values(by='NORM')
    df_control = df_control.reset_index(drop=True)
    return df_control


def get_current_algorithm_test_dataset_using_pandas(code):
    try:
        test_data = MetAromatic(code=code, angle=ANGLE_483_TESTS, cutoff=CUTOFF_483_TESTS).met_aromatic()
    except IndexError:
        skip('Skipping list index out of range error. Occurs because of missing data.')
    else:
        df_test = DataFrame(test_data, columns=COLUMNS_483_TESTS)
        df_test = df_test.reindex(sorted(df_test.columns), axis=1)
        df_test = df_test.sort_values(by='NORM')
        df_test = df_test.reset_index(drop=True)
        df_test = df_test.astype({'MET RES': 'int64', 'ARO RES': 'int64'})
        return df_test


@mark.parametrize("code", set(CONTROL_483_DATA_DF.PDBCODE))
def test_metaromatic_algorithm_against_483_data(code):
    df_control = get_ma_2_483_control_dataset_using_pandas(code=code)
    df_test = get_current_algorithm_test_dataset_using_pandas(code=code)
    testing.assert_frame_equal(df_control, df_test)
