import unittest
from miniverse.service.rest.tools import parse_status, py_to_flask
from miniverse.service.urldefines import USER_GET_URI


class TestRestTools(unittest.TestCase):

    def test_parse_status(self):
        self.assertEqual(200, parse_status(200))
        self.assertEqual(200, parse_status("200"))
        self.assertEqual(201, parse_status("201 WITH CREATED"))

    def test_py_to_flask(self):
        self.assertEqual("/user/<user_id>", py_to_flask(USER_GET_URI))

if __name__ == "__main__":
    unittest.main()
