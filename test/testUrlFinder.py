from unittest import TestCase
from .onyxparser.htmlParser.url import UrlFinder
from resource import resource

class testUrlFinder(TestCase):

    def setUp(self):
        import getpass
        self.settings = resource.request_settings()
        self.buildRequests()
        self.settings.setProxyHandler(user=getpass.getuser(),password='')

    def buildRequests(self):
        self.settings.setAgent()
        self.settings.setCharset()
        self.req = resource.Request(self.settings)

    def testTradeNosishtml(self):
        urls = []
        self.req.getRequest('http://trade.nosis.com/es/q?query=20215487270')
        for url in UrlFinder(self.req).get_urls():
            if 'FAB' in url:
                urls.append(url)
        self.assertEqual(len(urls),1)
        self.assertEqual('/es/OLEGO-FABRICIO-ARIEL/20215487270/1/p?pos=1&query=20215487270',urls[0])


