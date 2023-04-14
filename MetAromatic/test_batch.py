from os import EX_OK
from pathlib import Path
import pytest
from click.testing import CliRunner
from pymongo import MongoClient, errors
from runner import cli

HOST_MONGODB = 'localhost'
PORT_MONGODB = 27017
TIMEOUT_MONGODB_MSEC = 1000


@pytest.mark.test_command_line_interface
class TestParallelProcessing:

    def setup_class(self):

        self.db_name = 'database_coronavirus'
        self.col_name = 'collection_coronavirus'

        self.client = MongoClient(host=HOST_MONGODB, port=PORT_MONGODB)

        try:
            self.client.list_databases()
        except errors.OperationFailure as e:
            pytest.skip(str(e))
        except errors.ServerSelectionTimeoutError as e:
            pytest.exit(str(e))

        self.cursor = self.client[self.db_name][self.col_name]

        test_data = Path(__file__).resolve().parent / 'core' / 'test_data' / 'data_coronavirus_entries.txt'

        if not test_data.exists():
            pytest.exit(f'File {test_data} is missing')

        self.threads = 3

        command = f'batch {test_data} --threads={self.threads} --database={self.db_name} --collection={self.col_name}'

        runner = CliRunner()
        result = runner.invoke(cli, command.split())

        if result.exit_code != EX_OK:
            pytest.fail('Batch job exited with non-zero exit code')

        self.num_coronavirus_entries = 9

        info_collection = self.client[self.db_name][self.col_name + '_info']
        self.results_info = list(info_collection.find())[0]

    def teardown_class(self):
        self.client.drop_database(self.db_name)

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
        collections = self.client[self.db_name].list_collection_names()
        assert self.col_name + '_info' in collections

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
