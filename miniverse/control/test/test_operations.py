import inspect
import os
import unittest
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from miniverse.control.operations import create_user, get_user, get_user_balance
from miniverse.model.model import Base
import miniverse.control.test as test_module


class TestOperations(unittest.TestCase):
    TEST_DB = 'test_miniverse_operations.db'

    @classmethod
    def setUpClass(cls):
        # get test data folder
        cls.data_folder = os.path.join(os.path.dirname(inspect.getfile(test_module)), "data")

    def setUp(self):
        # Populate the DB
        engine = create_engine('sqlite:///'+TestOperations.TEST_DB)
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()


    def test_user_creation_retrieval(self):
        user_uri = create_user(self.session, "peter", "--------", 3.0)
        user_json = get_user(self.session, "peter")
        del user_json["created"]
        self.assertEqual("/user/peter", user_uri)
        expected_json = {
            'funds': 3.0,
            'pass_hash': '--------',
            'picture_path': None,
            'name': 'peter'
        }
        self.assertDictEqual(expected_json, user_json)
        peter_balance = get_user_balance(self.session, "peter")
        self.assertEqual(3.0, peter_balance)

if __name__ == '__main__':
    unittest.main()