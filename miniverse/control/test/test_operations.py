import inspect
import os
import unittest
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from miniverse.control.operations import create_user, get_user, get_user_balance, create_movement, get_movement, \
    update_user_funds, check_user_has_enough_money, create_transfer, get_transfer
from miniverse.model.exceptions import NotEnoughMoneyException
from miniverse.model.model import Base, MovementType, TransferType
import miniverse.control.test as test_module


class TestOperations(unittest.TestCase):
    TEST_DB = 'test_miniverse_operations.db'

    @classmethod
    def setUpClass(cls):
        # get test data folder
        cls.data_folder = os.path.join(os.path.dirname(inspect.getfile(test_module)), "data")

    def setUp(self):
        # Populate the DB
        if os.path.exists(TestOperations.TEST_DB):
            os.remove(TestOperations.TEST_DB)
        engine = create_engine('sqlite:///' + TestOperations.TEST_DB)
        #Base.metadata.drop_all(bind=engine)
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
        del movement_json["created"]
        expected_json = {
            'amount': -10.0,
            'type': 'FUNDS_WITHDRAWAL',
            'user': '/user/dean',
            'id': 1
        }
        self.assertDictEqual(expected_json, movement_json)

        # Retrieval with expansion
        movement_json = get_movement(self.session, movement_id, expand=True)
        del movement_json["created"]
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
        pep_uri = create_user(self.session, "pep", "0123456789ABCDEF", 100.0)
        user_id = pep_uri.split("/")[-1]
        check_user_has_enough_money(self.session, user_id, -90)
        with self.assertRaises(NotEnoughMoneyException):
            check_user_has_enough_money(self.session, user_id, -110)

    def test_update_user_funds(self):
        pep_uri = create_user(self.session, "pep", "0123456789ABCDEF", 100.0)
        user_id = pep_uri.split("/")[-1]
        update_user_funds(self.session, user_id, 10.)
        pep_json = get_user(self.session, user_id)
        self.assertEqual(110.0, pep_json["funds"])

    def test_create_retrieve_transfer(self):
        # susan -> 25 -> pep, Susan gives 25 to Pep

        # Create the users
        susan_uri = create_user(self.session, "susan", "0123456789ABCDEF", 100.0)
        susan_id = susan_uri.split("/")[-1]
        pep_uri = create_user(self.session, "pep", "0123456789ABCDEF", 50.0)
        pep_id = pep_uri.split("/")[-1]

        # Create the movements
        susan_movement_uri = create_movement(self.session, susan_uri, -25,
                                         movement_type=MovementType.TRANSFER_WITHDRAWAL,
                                         commit=False)
        pep_movement_uri = create_movement(self.session, pep_uri, 25,
                                           movement_type=MovementType.TRANSFER_DEPOSIT,
                                           commit=False)

        transfer_uri = create_transfer(self.session, susan_movement_uri, pep_movement_uri,
                                       "Great lunch!!",
                                       TransferType.PUBLIC)
        self.assertEqual("/transfer/1", transfer_uri)

        # Retrieve the transfer
        transfer_json = get_transfer(self.session, 1)
        del transfer_json["created"]
        expected = {
            'comment': 'Great lunch!!',
            'deposit': '/movement/2',
            'withdrawal': '/movement/1',
            'type': 'PUBLIC',
            'id': 1
        }
        self.assertDictEqual(expected, transfer_json)

        # Try expanding the movements
        transfer_json = get_transfer(self.session, 1, expand=True)
        expected = {
            'comment': 'Great lunch!!',
            'deposit': {
                'amount': 25.0,
                'type': 'TRANSFER_DEPOSIT',
                'user': '/user/pep',
                'id': 2},
            'withdrawal': {
                'amount': -25.0,
                'type': 'TRANSFER_WITHDRAWAL',
                'user': '/user/susan',
                'id': 1
            },
            'type': 'PUBLIC',
            'id': 1
        }
        del transfer_json["created"]
        del transfer_json["withdrawal"]["created"]
        del transfer_json["deposit"]["created"]
        self.assertDictEqual(expected, transfer_json)

        # Also, after the transfer susan and pep have the same amount of money
        self.assertEqual(get_user_balance(self.session, susan_id), get_user_balance(self.session, pep_id))
        self.assertEqual(75., get_user_balance(self.session, susan_id))

if __name__ == '__main__':
    unittest.main()
