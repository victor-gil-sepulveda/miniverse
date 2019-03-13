import inspect
import os
import unittest
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from miniverse.control.operations import create_user, get_user, get_user_balance, create_movement, get_movement
from miniverse.model.model import Base, MovementType
import miniverse.control.test as test_module


class TestOperations(unittest.TestCase):
    TEST_DB = 'test_miniverse_operations.db'

    @classmethod
    def setUpClass(cls):
        # get test data folder
        cls.data_folder = os.path.join(os.path.dirname(inspect.getfile(test_module)), "data")

    def setUp(self):
        # Populate the DB
        engine = create_engine('sqlite:///' + TestOperations.TEST_DB)
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

    def test_movement_creation_retrieval(self):
        # Resource creation
        dean_uri = create_user(self.session, "dean", "0123456789ABCDEF", 100.0)
        movement_uri = create_movement(self.session, dean_uri, -10, movement_type=MovementType.FUNDS_WITHDRAWAL)
        self.assertEqual('/movement/1', movement_uri)

        # Resource retrieval
        movement_id = int(movement_uri.split("/")[-1])
        movement_json = get_movement(self.session, movement_id)
        expected_json = {
            'amount': -10.0,
            'type': 'FUNDS_WITHDRAWAL',
            'user': '/user/dean',
            'id': 1
        }
        self.assertDictEqual(expected_json, movement_json)

        # Retrieval with expansion
        movement_json = get_movement(self.session, movement_id, expand=True)
        del movement_json["user"]["created"]
        expected_json = {
            'amount': -10.0,
            'type': 'FUNDS_WITHDRAWAL',
            'user': {
                'funds': 90.0,
                'pass_hash': '0123456789ABCDEF',
                'picture_path': None,
                'name': 'dean'
            },
            'id': 1
        }

        self.assertDictEqual(expected_json, movement_json)

        print movement_json

    def test_check_user_has_enough_money(self):
        pass

if __name__ == '__main__':
    unittest.main()
