from unittest import TestCase
from resource import resource
from useful.singleton import forgetAllSingletons


class TestRequest(TestCase):
    def setUp(self):
        self.settings = None
        self.linkses = ['http://www.google.com.ar/search']
        self.req = resource.Request(self.settings)

    def tearDown(self):
        forgetAllSingletons()

    def test(self):
        self.req.postRequest(self.linkses[0], values={'q': 'bleh'})
        self.req.getRequestDebug()