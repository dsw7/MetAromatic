from os import path
from subprocess import (
    call,
    DEVNULL
)
from pytest import (
    mark,
    fail,
    skip
)
from pymongo import MongoClient
from .helpers.consts import (
    EXIT_SUCCESS,
    EXIT_FAILURE
)

HOST_MONGODB = 'localhost'
PORT_MONGODB = 27017
TIMEOUT_MONGODB_MSEC = 1000


@mark.test_command_line_interface
class TestParallelProcessing:

    def setup_class(self):

        project_root = path.dirname(path.abspath(__file__))
        path_runner = path.join(path.dirname(project_root), 'runner.py')
        path_test_data = path.join(project_root, 'helpers', 'data_coronavirus_entries.txt')

        if not path.exists(path_test_data):
            fail('Path {} does not exist'.format(path_test_data))

        self.threads = 3
        self.database_name = 'database_coronavirus'
        self.collection_name = 'collection_coronavirus'

        command = '{} batch {} '.format(path_runner, path_test_data)
        command += '--threads {} '.format(self.threads)
        command += '--database {} '.format(self.database_name)
        command += '--collection {}'.format(self.collection_name)

        #if call(command.split(), stdout=DEVNULL, stderr=DEVNULL) != EXIT_SUCCESS:
        if call(command.split()) != EXIT_SUCCESS:
            skip('Cannot proceed with test. Could not connect to a mongod instance')

        self.num_coronavirus_entries = 9
        self.client = MongoClient(host=HOST_MONGODB, port=PORT_MONGODB)
        self.cursor = self.client[self.database_name][self.collection_name]

    def teardown_class(self):
        self.client.drop_database(self.database_name)

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
