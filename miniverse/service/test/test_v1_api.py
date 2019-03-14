import json
import unittest
from flask.app import Flask
from flask_api import status

from miniverse.model.model import TransactionType, TransferType
from miniverse.service.rest import v1
from miniverse.control.operations import create_user, get_user_balance, create_transaction
from miniverse.model.sessionsingleton import DbSessionHolder
from miniverse.service.rest.api import setup_rest_api, gen_resource_url, API_PREFIX
from miniverse.service.rest.tools import parse_status
from miniverse.service.urldefines import USER_POST_URI, USER_GET_URI, USER_GET_BALANCE_URI, TRANSACTION_POST_URI, \
    TRANSFER_POST_URI, USER_GET_TRANSACTIONS_URI, USER_GET_EXPANDED_TRANSACTIONS_URI


class TestV1API(unittest.TestCase):

    REST_TEST_DB = "miniverse_rest_api_test.db"

    def setUp(self):
        app = Flask(__name__)
        app.testing = True
        app.config["TESTING"] = True

        setup_rest_api(app)
        self.client = app.test_client

        # Init db
        DbSessionHolder('sqlite:///' + TestV1API.REST_TEST_DB).reset()

    def test_user_creation(self):
        endpoint = gen_resource_url(API_PREFIX, v1, USER_POST_URI)

        # Adding a new user returns 201
        response = self.client().post(endpoint, data=json.dumps({
            "name": "susan",
            "phone_number": "0000",
            "pass_hash": "1111"
        }))

        self.assertEqual(status.HTTP_201_CREATED, parse_status(response.status))
        self.assertEqual(USER_GET_URI.format(user_id="0000"), response.location)
        self.assertDictEqual({"name": "susan", "phone_number": "0000", "pass_hash": "1111"}, json.loads(response.data))

        # Adding a user with an already stored phone number is not allowed
        response = self.client().post(endpoint, data=json.dumps({
            "name": "pep",
            "phone_number": "0000",
            "pass_hash": "213124"
        }))
        self.assertEqual(status.HTTP_409_CONFLICT, parse_status(response.status))

    def test_balance(self):
        create_user(DbSessionHolder(TestV1API.REST_TEST_DB).get_session(),
                    "0000",
                    "Finn",
                    "1413434",
                    233.05)

        endpoint = gen_resource_url(API_PREFIX, v1, USER_GET_BALANCE_URI.format(user_id="0000"))
        response = self.client().get(endpoint)
        expected = {
            "balance": 233.05,
            "user": "/user/0000"
        }

        self.assertDictEqual(expected, json.loads(response.data))

    def test_create_transaction(self):
        session = DbSessionHolder(TestV1API.REST_TEST_DB).get_session()
        create_user(session,
                    "0000",
                    "Finn",
                    "1413434",
                    233.05)

        endpoint = gen_resource_url(API_PREFIX, v1, TRANSACTION_POST_URI)
        response = self.client().post(endpoint, data=json.dumps({
            "user": "0000",
            "amount": 52,
            "type": TransactionType.FUNDS_DEPOSIT
        }))
        self.assertEqual("/transaction/1", response.headers["location"])

        # The user balance has changed
        finn_balance = get_user_balance(session, "0000") # Finn's phone is his ID
        self.assertEqual(285.05, finn_balance)

        error_response_1 = self.client().post(endpoint, data=json.dumps({
            "user": "0000",
            "amount": 0,
            "type": TransactionType.FUNDS_DEPOSIT
        }))
        self.assertEqual('{"error":"If no money is moved, this is not a money transaction!"}', error_response_1.data.strip())
        error_response_2 = self.client().post(endpoint, data=json.dumps({
            "user": "0000",
            "amount": -300,
            "type": TransactionType.FUNDS_DEPOSIT
        }))
        self.assertEqual('{"error":"Not enough money in your wallet!"}', error_response_2.data.strip())

    def test_create_transfer(self):
        session = DbSessionHolder(TestV1API.REST_TEST_DB).get_session()
        finn_uri = create_user(session,
                               "0000",
                               "Finn",
                               "1413434",
                               233.05)

        jake_uri = create_user(session,
                               "0001",
                               "Jake",
                               "1413434",
                               60.)

        transfer_data = {
            "sender": finn_uri,
            "receiver": jake_uri,
            "amount": 13.05,
            "comment": "I want to get ride of small coins!",
            "type": TransferType.PUBLIC
        }

        endpoint = gen_resource_url(API_PREFIX, v1, TRANSFER_POST_URI)
        response = self.client().post(endpoint, data=json.dumps(transfer_data))
        self.assertEqual("/transfer/1", response.headers["location"])
        finn_balance = get_user_balance(session, "0000")
        jake_balance = get_user_balance(session, "0001")
        self.assertEqual((220.05, 73.0), (finn_balance, jake_balance))

    def test_get_user_transactions(self):
        session = DbSessionHolder(TestV1API.REST_TEST_DB).get_session()
        finn_uri = create_user(session,
                               "0000",
                               "Finn",
                               "1413434",
                               233.05)
        create_transaction(session, amount=10, user_uri=finn_uri, transaction_type=TransactionType.FUNDS_DEPOSIT)
        create_transaction(session, amount=3, user_uri=finn_uri, transaction_type=TransactionType.FUNDS_DEPOSIT)
        create_transaction(session, amount=-4.05, user_uri=finn_uri, transaction_type=TransactionType.FUNDS_WITHDRAWAL)

        endpoint = gen_resource_url(API_PREFIX, v1, USER_GET_TRANSACTIONS_URI.format(user_id="0000"))
        response = self.client().get(endpoint)
        self.assertItemsEqual(["/transaction/1", "/transaction/2", "/transaction/3"], json.loads(response.data))

        endpoint = gen_resource_url(API_PREFIX, v1, USER_GET_EXPANDED_TRANSACTIONS_URI.format(user_id="0000"))
        response = self.client().get(endpoint)
        expected = [
            {"amount": 10.0, "id": 1, "type": "FUNDS_DEPOSIT", "user": "/user/0000"},
            {"amount": 3.0, "id": 2, "type": "FUNDS_DEPOSIT", "user": "/user/0000"},
            {"amount": -4.05, "id": 3, "type": "FUNDS_WITHDRAWAL", "user": "/user/0000"}
        ]
        parsed_response = json.loads(response.data)
        for mov in parsed_response:
            del mov["created"]
        self.assertItemsEqual(expected, parsed_response)


if __name__ == "__main__":
    unittest.main()
