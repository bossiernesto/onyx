from resource.RequestStatistics import RequestStatistics
from resource.resource import *
import unittest

class TestStatistics(unittest.TestCase):

    def setUp(self):
        self.statistics=RequestStatistics.getInstance()
        self.settings=request_settings(statistics=True)
        self.buildRequests()
        self.linkses=['http://es.wikipedia.org/wiki/','http://fluxbox.org/']

    def tearDown(self):
        self.statistics.clearStatistics()

    def buildRequests(self):
        self.settings.setAgent()
        self.settings.setCharset()
        import getpass
        self.settings.setProxyHandler(user=getpass.getuser(),password='mongo2013')
        self.req=Request(self.settings)

    def testLogStatistics(self):
        for link in self.linkses:
            self.req.getRequest(link)
        self.assertEqual(self.statistics.hits,2)

    def testDownloadedStatistics(self):
        redirlink='http://goo.gl/bKZxu' #PyPI redirection with goo.gl
        self.req.getRequest(redirlink)
        self.assertGreater(self.statistics.downloaded,21950)

    def testRedirectStatistics(self):
        redirlink='http://goo.gl/bKZxu' #PyPI redirection with goo.gl
        self.req.getRequest(redirlink)
        self.assertEqual(self.statistics.redirects,1)

    def testHitsAndRedirections(self):
        linkRedirect='http://goo.gl/gK3uW'
        self.req.getRequest(linkRedirect)
        self.req.getRequest(self.linkses[0])
        self.assertEqual(self.statistics.hits,2)