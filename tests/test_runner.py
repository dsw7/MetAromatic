from subprocess import call
from pymongo import MongoClient
from pandas import DataFrame, read_csv, testing


CLIENT = MongoClient(port=27017, host='localhost')
DEFAULT_DB = 'foo'
DEFAULT_COL = 'bar'
PATH_TEST_CODES = 'controls/runner_test_codes.txt'
PATH_TEST_DATA = 'controls/runner_test_data.csv'
CMD_ROOT = "python3 ../metaromatic/runner.py --batch {}".format(PATH_TEST_CODES)
CUSTOM_DB = 'hamspam'
CUSTOM_COL = 'foobar'


def test_runner_mongo_default_settings():
    CLIENT.drop_database(DEFAULT_DB)
    cmd = CMD_ROOT + " --export-mongo"
    call(cmd.split())
    test_data = CLIENT[DEFAULT_DB][DEFAULT_COL].find()
    dataframe_test = DataFrame(test_data)
    dataframe_test = dataframe_test[['norm', 'met-phi', 'met-theta']]
    dataframe_test = dataframe_test.sort_values(by='norm')
    dataframe_test = dataframe_test.reset_index(drop=True)
    dataframe_control = read_csv(PATH_TEST_DATA)
    dataframe_control = dataframe_control[['norm', 'met-phi', 'met-theta']]
    testing.assert_frame_equal(dataframe_test, dataframe_control)
    CLIENT.drop_database(DEFAULT_DB)


def test_runner_mongo_custom_settings():
    CLIENT.drop_database(DEFAULT_DB)
    cmd = CMD_ROOT + " --export-mongo --database {} --collection {}".format(CUSTOM_DB, CUSTOM_COL)
    call(cmd.split())
    test_data = CLIENT[CUSTOM_DB][CUSTOM_COL].find()
    dataframe_test = DataFrame(test_data)
    dataframe_test = dataframe_test[['norm', 'met-phi', 'met-theta']]
    dataframe_test = dataframe_test.sort_values(by='norm')
    dataframe_test = dataframe_test.reset_index(drop=True)
    dataframe_control = read_csv(PATH_TEST_DATA)
    dataframe_control = dataframe_control[['norm', 'met-phi', 'met-theta']]
    testing.assert_frame_equal(dataframe_test, dataframe_control)
    CLIENT.drop_database(CUSTOM_DB)
