import unittest
from config.AppContext import *
from useful import singleton


class A:
    pass


class AppContextTestCase(unittest.TestCase):
    def setUp(self):
        self.app = appContext.getInstance()
        self.app.build_defaultsettings()

    def tearDown(self):
        singleton.forgetAllSingletons()

    def test_sectionlen(self):
        self.assertEqual(6, len([section for section in self.app.config_parser.sections()]))

    def test_sectionExists(self):
        self.assertTrue(self.app.sectionExists(CONTAINER_SECTION))

    def test_getVersion(self):
        self.assertEqual("http://localhost:5984", self.app.getValue("COUCH_DB_NAME"))

    def test_setvalue(self):
        a = A()
        self.app.set_object(A, a)
        klass = str(a.__class__).split('.')[1]
        aInst = self.app.getObject(klass)
        self.assertEqual(a, aInst)

    def test_setObject(self):
        pass

    def test_AppContextSingleton(self):
        appCon = appContext.getInstance()
        self.assertEqual(appCon, self.app)


if __name__ == '__main__':
    unittest.main()