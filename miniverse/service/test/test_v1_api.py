import unittest
from flask.app import Flask
import json
from flask_api import status
import random
import string

from miniverse.model.sessionsingleton import DbSessionHolder
from miniverse.service.rest import v1
from miniverse.service.rest.api import setup_rest_api, gen_resource_url, API_PREFIX
from miniverse.service.rest.tools import parse_status


class TestV1API(unittest.TestCase):

    REST_TEST_DB = "miniverse_rest_api_test.db"

    def setUp(self):
        app = Flask(__name__)
        app.testing = True
        app.config["TESTING"] = True

        setup_rest_api(app)
        self.client = app.test_client

        # Init db
        DbSessionHolder(TestV1API.REST_TEST_DB).reset()

    def test_user_creation(self):
        endpoint = gen_resource_url(API_PREFIX, v1, "/user")

        # Adding a new user returns 201
        response = self.client().post(endpoint, data=json.dumps({
            "name": "susan",
            "phone_number": "0000",
            "pass_hash": "1111"
        }))

        self.assertEqual(status.HTTP_201_CREATED, parse_status(response.status))
        self.assertEqual("/user/0000", response.location)
        self.assertDictEqual({"name": "susan", "phone_number": "0000", "pass_hash": "1111"}, json.loads(response.data))

        # Adding a user with an already stored phone number is not allowed
        response = self.client().post(endpoint, data=json.dumps({
            "name": "pep",
            "phone_number": "0000",
            "pass_hash": "213124"
        }))
        self.assertEqual(status.HTTP_409_CONFLICT, parse_status(response.status))



if __name__ == "__main__":
    unittest.main()
