import unittest
from miniverse.service.rest.tools import parse_status


class TestRestTools(unittest.TestCase):

    def test_parse_status(self):
        self.assertEqual(200, parse_status(200))
        self.assertEqual(200, parse_status("200"))
        self.assertEqual(201, parse_status("201 WITH CREATED"))

if __name__ == "__main__":
    unittest.main()
