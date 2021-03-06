from os import path
from subprocess import call, DEVNULL
from pymongo import MongoClient
from .consts import (
    EXIT_SUCCESS,
    EXIT_FAILURE
)

class TestBatchJob:
    def setup_class(self):
        project_root = path.dirname(path.dirname(path.abspath(__file__)))
        path_runner = path.join(project_root, 'runner.py')
        path_test_data = path.join(project_root, 'utils/test_data/coronavirus_test_entries.txt')
        self.threads = 3
        self.num_coronavirus_entries = 9
        self.database_name = 'database_coronavirus'
        self.collection_name = 'collection_coronavirus'
        self.client = MongoClient(host='localhost', port=27017)
        self.cursor = self.client[self.database_name][self.collection_name]

        cmd = (
            f'{path_runner} run-batch-job {path_test_data} '
            f'--threads {self.threads} '
            f'--database {self.database_name} '
            f'--collection {self.collection_name}'
        )
        call(cmd.split(), stdout=DEVNULL, stderr=DEVNULL)

    def test_correct_count(self):
        assert len(list(self.cursor.find())) == self.num_coronavirus_entries

    def test_correct_exit_code_2ca1(self):
        assert list(self.cursor.find({'_id': '2ca1'}))[0]['exit_code'] == EXIT_SUCCESS

    def test_correct_exit_code_2fyg(self):
        assert list(self.cursor.find({'_id': '2fyg'}))[0]['exit_code'] == EXIT_SUCCESS

    def test_correct_exit_status_2ca1(self):
        assert list(self.cursor.find({'_id': '2ca1'}))[0]['exit_status'] == 'Success'

    def test_correct_exit_status_2fyg(self):
        assert list(self.cursor.find({'_id': '2fyg'}))[0]['exit_status'] == 'Success'

    def test_correct_exit_code_1xak(self):
        assert list(
            self.cursor.find({'_id': '1xak'})
        )[0]['exit_code'] == EXIT_FAILURE

    def test_correct_exit_code_2fxp(self):
        assert list(
            self.cursor.find({'_id': '2fxp'})
        )[0]['exit_code'] == EXIT_FAILURE

    def test_correct_exit_code_6mwm(self):
        assert list(
            self.cursor.find({'_id': '6mwm'})
        )[0]['exit_code'] == EXIT_FAILURE

    def test_correct_exit_code_2cme(self):
        assert list(
            self.cursor.find({'_id': '2cme'})
        )[0]['exit_code'] == EXIT_FAILURE

    def test_correct_exit_code_spam(self):
        assert list(
            self.cursor.find({'_id': 'spam'})
        )[0]['exit_code'] == EXIT_FAILURE

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

    def teardown_class(self):
        self.client.drop_database(self.database_name)
