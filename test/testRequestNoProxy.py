from unittest import TestCase
from resource import resource
from useful.singleton import forgetAllSingletons
import os


class TestRequest(TestCase):
    def setUp(self):
        self.settings = resource.request_settings()
        self.req = resource.Request(self.settings)
        self.linkses = ['http://es.wikipedia.org/wiki/']
        self.linkFile = 'http://malc0de.com/bl/BOOT'
        self.link_redirect = 'http://goo.gl/gK3uW'

    def tearDown(self):
        forgetAllSingletons()

    def testZip(self):
        self.req.getRequest('http://css3menu.com/download/winff5jo0awd')
        os.remove('css3menu-setup.zip')

    def testImage(self):
        self.req.getRequest(
            'http://www.autoweek.com/storyimage/CW/20121126/LOSANGELES/121129926/AR/0/2014-Ford-Fiesta-ST-LA-auto-show.jpg')
        os.remove('2014-Ford-Fiesta-ST-LA-auto-show.jpg')

    def testReturn(self):
        #To test the decorated getRequest method
        data = self.req.getRequest(self.linkses[0])
        self.assertEqual(data, self.req.html)
        self.assertEqual(len(self.req.history), 2)

    def testStatus(self):
        self.req.getRequest(self.linkses[0])
        self.assertEqual(self.req.status_code, 200)
        self.assertEqual(self.req.info.getheader("Content-Language"), "es")

    def testIsFile(self):
        self.req.getRequest(self.linkFile)
        self.assertTrue(self.req.isFile)

    def testPersistanceFile(self):
        self.req.getRequest(self.linkFile)
        self.assertTrue(os.path.exists("BOOT"))
        os.remove("BOOT")

    def testPdfPersistance(self):
        file = "PasoaPasoSIRADiG.pdf"
        afipPDF = 'www.afip.gob.ar/572web/documentos/PasoaPasoSIRADiG.pdf'
        self.req.getRequest(afipPDF)
        self.assertTrue(os.path.exists(file))
        os.remove(file)

    def testRedirect(self):
        self.req.getRequest(self.link_redirect)
        self.assertEqual(len(self.req.history), 2)
        self.assertEqual(self.req.status_code, 200)

    def testNoRedirect(self):
        self.settings = resource.request_settings(redirects=False)
        self.req.settings = self.settings #Override setting
        self.req.getRequest(self.link_redirect)
        self.assertEqual(self.req.status_code, 301)
        self.assertEqual(len(self.req.history), 1)

    def testJson(self):
        import json

        data = self.req.getRequest('https://github.com/timeline.json')
        jsondata = json.loads(data)
        self.assertTrue(hasattr(self.req, 'json'))
        self.assertEqual(jsondata, self.req.json())
