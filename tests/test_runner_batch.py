from os import EX_OK
from pathlib import Path
from pytest import exit, fail, skip
from click.testing import CliRunner
from pymongo import MongoClient, errors
from MetAromatic.runner import cli

HOST_MONGODB = 'localhost'
PORT_MONGODB = 27017
DB_NAME = 'database_coronavirus'
COL_NAME = 'collection_coronavirus'
TEST_DATA = Path(__file__).resolve().parent / 'data_coronavirus_entries.txt'

if not TEST_DATA.exists():
    exit(f'File {TEST_DATA} is missing')


class TestRunnerBatch:

    def setup_class(self):
        self.runner = CliRunner()

    def test_batch_too_few_threads(self):
        command = f'batch {TEST_DATA} --threads=-1 --database={DB_NAME} --collection={COL_NAME}'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK

    def test_batch_too_many_threads(self):
        command = f'batch {TEST_DATA} --threads=100 --database={DB_NAME} --collection={COL_NAME}'

        result = self.runner.invoke(cli, command.split())
        assert result.exit_code != EX_OK


class TestParallelProcessing:

    def setup_class(self):

        self.client = MongoClient(host=HOST_MONGODB, port=PORT_MONGODB)

        try:
            self.client.list_databases()
        except errors.OperationFailure as e:
            skip(str(e))
        except errors.ServerSelectionTimeoutError as e:
            exit(str(e))

        self.cursor = self.client[DB_NAME][COL_NAME]
        self.threads = 3

        command = f'batch {TEST_DATA} --threads={self.threads} --database={DB_NAME} --collection={COL_NAME}'

        runner = CliRunner()
        result = runner.invoke(cli, command.split())

        if result.exit_code != EX_OK:
            fail('Batch job exited with non-zero exit code')

        self.num_coronavirus_entries = 9

        info_collection = self.client[DB_NAME][COL_NAME + '_info']
        self.results_info = list(info_collection.find())[0]

    def teardown_class(self):
        self.client.drop_database(DB_NAME)

    def test_correct_count(self):
        assert len(list(self.cursor.find())) == self.num_coronavirus_entries

    def test_correct_exit_code_2ca1(self):
        assert list(self.cursor.find({'_id': '2ca1'}))[0]['ok']

    def test_correct_exit_code_2fyg(self):
        assert list(self.cursor.find({'_id': '2fyg'}))[0]['ok']

    def test_correct_exit_status_2ca1(self):
        assert list(self.cursor.find({'_id': '2ca1'}))[0]['status'] == 'Success'

    def test_correct_exit_status_2fyg(self):
        assert list(self.cursor.find({'_id': '2fyg'}))[0]['status'] == 'Success'

    def test_correct_exit_code_1xak(self):
        assert not list(self.cursor.find({'_id': '1xak'}))[0]['ok']

    def test_correct_exit_code_2fxp(self):
        assert not list(self.cursor.find({'_id': '2fxp'}))[0]['ok']

    def test_correct_exit_code_6mwm(self):
        assert not list(self.cursor.find({'_id': '6mwm'}))[0]['ok']

    def test_correct_exit_code_2cme(self):
        assert not list(self.cursor.find({'_id': '2cme'}))[0]['ok']

    def test_correct_exit_code_spam(self):
        assert not list(self.cursor.find({'_id': 'spam'}))[0]['ok']

    def test_info_file_in_results(self):
        collections = self.client[DB_NAME].list_collection_names()
        assert COL_NAME + '_info' in collections

    def test_info_file_correct_num_workers(self):
        assert self.results_info['num_workers'] == self.threads

    def test_info_file_correct_number_of_entries(self):
        assert self.results_info['number_of_entries'] == self.num_coronavirus_entries

    def test_info_file_correct_chain(self):
        assert self.results_info['chain'] == 'A'

    def test_info_file_correct_model(self):
        assert self.results_info['model'] == 'cp'

    def test_info_file_correct_cutoff_distance(self):
        assert self.results_info['cutoff_distance'] == 4.9

    def test_info_file_correct_cutoff_angle(self):
        assert self.results_info['cutoff_angle'] == 109.5
