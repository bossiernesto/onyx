import unittest

from


class RequestTestCase(unittest.TestCase):

    def __init__(self):
        self.pool = HTTPPoolConnection()

    def test_simple_request(self):
        response = self.pool_request('GET', 'http://www.example.com/')
        self.assertEqual(response.status, 200)