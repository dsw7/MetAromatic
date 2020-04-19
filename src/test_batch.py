from os import path
from subprocess import call, DEVNULL
from pymongo import MongoClient
from utilities import errors


class TestBatchJob:
    def setup_class(self):
        project_root = path.dirname(path.dirname(path.abspath(__file__)))
        path_runner = path.join(project_root, 'runner.py')
        path_test_data = path.join(project_root, 'src/test_data/coronavirus_test_entries.txt')
        threads = 3
        self.database_name = 'database_coronavirus'
        self.collection_name = 'collection_coronavirus'
        self.client = MongoClient(host='localhost', port=27017)
        cmd = (
            f'python {path_runner} '
            f'--batch '
            f'--threads {threads} '
            f'--batch_file {path_test_data} '
            f'--database {self.database_name} '
            f'--collection {self.collection_name}'
        )
        call(cmd.split(), stdout=DEVNULL, stderr=DEVNULL)

    def test_correct_count(self):
        cursor = self.client[self.database_name][self.collection_name]
        assert len(list(cursor.find())) == 9

    def test_correct_error_code_1xak(self):
        cursor = self.client[self.database_name][self.collection_name]
        assert list(
            cursor.find({'_id': '1xak'})
        )[0]['error_code'] == errors.ErrorCodes.NoMetCoordinatesError

    def test_correct_error_code_2fxp(self):
        cursor = self.client[self.database_name][self.collection_name]
        assert list(
            cursor.find({'_id': '2fxp'})
        )[0]['error_code'] == errors.ErrorCodes.NoMetCoordinatesError

    def test_correct_error_code_6mwm(self):
        cursor = self.client[self.database_name][self.collection_name]
        assert list(
            cursor.find({'_id': '6mwm'})
        )[0]['error_code'] == errors.ErrorCodes.NoResultsError

    def test_correct_error_code_2cme(self):
        cursor = self.client[self.database_name][self.collection_name]
        assert list(
            cursor.find({'_id': '2cme'})
        )[0]['error_code'] == errors.ErrorCodes.NoResultsError

    def test_correct_error_code_spam(self):
        cursor = self.client[self.database_name][self.collection_name]
        assert list(
            cursor.find({'_id': 'spam'})
        )[0]['error_code'] == errors.ErrorCodes.InvalidPDBFileError

    def teardown_class(self):
        self.client.drop_database(self.database_name)
