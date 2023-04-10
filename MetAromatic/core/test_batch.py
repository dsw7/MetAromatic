from os import EX_OK
from pathlib import Path
from subprocess import call, DEVNULL
import pytest
from pymongo import MongoClient

HOST_MONGODB = 'localhost'
PORT_MONGODB = 27017
TIMEOUT_MONGODB_MSEC = 1000


@pytest.mark.test_command_line_interface
class TestParallelProcessing:

    def setup_class(self):

        test_data = Path(__file__).resolve().parent / 'test_data' / 'data_coronavirus_entries.txt'

        if not test_data.exists():
            pytest.fail(f'File {test_data} is missing')

        runner = Path(__file__).resolve().parent / 'runner.py'

        self.threads = 3
        self.database_name = 'database_coronavirus'
        self.collection_name = 'collection_coronavirus'

        command = f'{runner} batch {test_data} '
        command += f'--threads {self.threads} '
        command += f'--database {self.database_name} '
        command += f'--collection {self.collection_name}'

        if call(command.split(), stdout=DEVNULL, stderr=DEVNULL) != EX_OK:
            pytest.fail(f'Command "{command}" failed')

        self.num_coronavirus_entries = 9
        self.client = MongoClient(host=HOST_MONGODB, port=PORT_MONGODB)
        self.cursor = self.client[self.database_name][self.collection_name]

    def teardown_class(self):
        self.client.drop_database(self.database_name)

    def test_correct_count(self):
        assert len(list(self.cursor.find())) == self.num_coronavirus_entries

    def test_correct_exit_code_2ca1(self):
        assert list(self.cursor.find({'_id': '2ca1'}))[0]['exit_code'] == EX_OK

    def test_correct_exit_code_2fyg(self):
        assert list(self.cursor.find({'_id': '2fyg'}))[0]['exit_code'] == EX_OK

    def test_correct_exit_status_2ca1(self):
        assert list(self.cursor.find({'_id': '2ca1'}))[0]['exit_status'] == 'Success'

    def test_correct_exit_status_2fyg(self):
        assert list(self.cursor.find({'_id': '2fyg'}))[0]['exit_status'] == 'Success'

    def test_correct_exit_code_1xak(self):

        assert list(
            self.cursor.find({'_id': '1xak'})
        )[0]['exit_code'] != EX_OK

    def test_correct_exit_code_2fxp(self):

        assert list(
            self.cursor.find({'_id': '2fxp'})
        )[0]['exit_code'] != EX_OK

    def test_correct_exit_code_6mwm(self):

        assert list(
            self.cursor.find({'_id': '6mwm'})
        )[0]['exit_code'] != EX_OK

    def test_correct_exit_code_2cme(self):

        assert list(
            self.cursor.find({'_id': '2cme'})
        )[0]['exit_code'] != EX_OK

    def test_correct_exit_code_spam(self):

        assert list(
            self.cursor.find({'_id': 'spam'})
        )[0]['exit_code'] != EX_OK

    def test_info_file_in_results(self):
        collections = self.client[self.database_name].list_collection_names()

        assert self.collection_name + '_info' in collections

    def test_info_file_correct_num_workers(self):
        info_collection = self.client[self.database_name][self.collection_name + '_info']

        assert list(info_collection.find())[0]['num_workers'] == self.threads

    def test_info_file_correct_number_of_entries(self):
        info_collection = self.client[self.database_name][self.collection_name + '_info']

        assert list(
            info_collection.find()
        )[0]['number_of_entries'] == self.num_coronavirus_entries
