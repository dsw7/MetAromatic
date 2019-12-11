from sys import path; path.append('../metaromatic')
from pytest import mark, skip
from pandas import read_csv, DataFrame, testing
from ma3 import MetAromatic
from conftest import Setup


DISABLE_EC_TESTS = False
DISABLE_PROTEIN_ID_TESTS = True
DISABLE_BRIDGE_TESTS = True
DISABLE_MA_2_483_TESTS = True
CONTROL_EC_CODES = './controls/test_dataset_ec_codes.csv'
CONTROL_BRIDGE_DATA = './controls/test_n_3_bridges_no_ang_limit_6_angstroms.json'
CONTROL_483_DATA = './controls/test_483OutputA3-3-M-Benchmark_2.csv'
CONTROL_483_DATA_DF = read_csv(CONTROL_483_DATA)
ANGLE_BRIDGE_TESTS = 360.00
CUTOFF_BRIDGE_TESTS = 6.0
CUTOFF_483_TESTS = 4.9
ANGLE_483_TESTS = 109.5
CHAIN_483_TESTS = 'A'
COLUMNS_483_TESTS = ['ARO', 'ARO RES', 'MET', 'MET RES', 'NORM', 'MET-THETA', 'MET-PHI']


class TestMetAromatic:
    ec_data = Setup.get_control_ec_codes(CONTROL_EC_CODES)
    ec_ids = [i.get('pdb_code') for i in ec_data]
    @mark.skipif(DISABLE_EC_TESTS, reason='Skip if disabled')
    @mark.parametrize('ec', ec_data, ids=ec_ids)
    def test_ec_codes(self, ec):
        control_ec_code = ec.get('ec_code')
        test_ec_code = MetAromatic(ec.get('pdb_code')).get_ec_classifier()
        if control_ec_code == '':
            assert test_ec_code is None
        else:
            assert test_ec_code == control_ec_code


    protein_description_data = Setup.protein_identities
    protein_description_ids = [i.get('pdb_code') for i in protein_description_data]
    @mark.skipif(DISABLE_PROTEIN_ID_TESTS, reason='Skip if disabled')
    @mark.parametrize('identities', Setup.protein_identities, ids=protein_description_ids)
    def test_protein_identities(self, identities):
        assert MetAromatic(identities.get('pdb_code')).get_protein_identity() == identities.get('description')


    bridge_data = Setup.get_control_bridges(CONTROL_BRIDGE_DATA)
    bridge_data_ids = [i.get('pdb_code') for i in bridge_data]
    @mark.skipif(DISABLE_BRIDGE_TESTS, reason='Skip if disabled')
    @mark.parametrize('bridges', bridge_data, ids=bridge_data_ids)
    def test_bridge_collector(self, bridges):
        try:
            obj_bridges = MetAromatic(code=bridges.get('pdb_code'), angle=ANGLE_BRIDGE_TESTS, cutoff=CUTOFF_BRIDGE_TESTS)
            obj_bridges.met_aromatic()
        except IndexError:
            skip('Skipping list index out of range error. Occurs because of missing data.')
        else:
            assert set(bridges.get('bridge')) in obj_bridges.bridging_interactions(n=4)


    @staticmethod
    def get_ma_2_483_control_dataset_using_pandas(code):
        df_control = CONTROL_483_DATA_DF[CONTROL_483_DATA_DF.PDBCODE == code]
        df_control = df_control.drop(['PDBCODE'], axis=1)
        df_control = df_control.reindex(sorted(df_control.columns), axis=1)
        df_control = df_control.sort_values(by='NORM')
        df_control = df_control.reset_index(drop=True)
        return df_control


    @staticmethod
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


    @mark.skipif(DISABLE_MA_2_483_TESTS, reason='Skip if disabled')
    @mark.parametrize("code", set(CONTROL_483_DATA_DF.PDBCODE))
    def test_metaromatic_algorithm_against_483_data(self, code):
        df_control = self.get_ma_2_483_control_dataset_using_pandas(code=code)
        df_test = self.get_current_algorithm_test_dataset_using_pandas(code=code)
        testing.assert_frame_equal(df_control, df_test)
