from .persistance.documents import JSONDocument, XMLDocument, CSVDocument,json_session, csv_session, xml_session, FileDocument
import os
import unittest
from config.AppContext import appContext
from useful.singleton import forgetAllSingletons


class TestXMLDoc(XMLDocument):
    pass

class TestJSONDoc(JSONDocument):
    pass

class TestCSVDoc(CSVDocument):
    pass

class TestFileDoc(FileDocument):
    pass

class PersistanceTest(unittest.TestCase):

    def setUp(self):
        self.app=appContext.getInstance()
        self.app.build_defaultsettings()

    def tearDown(self):
            forgetAllSingletons()

    def test_XMLDocument(self):

        TestXMLDoc(attribute="test_value")
        TestXMLDoc(attribute="test_value2")
        xml_session.file_name = "data.xml"
        xml_session.commit()

        self.assertTrue(os.path.exists("data.xml"))
        os.remove("data.xml")

    def test_JSONDocument(self):

        TestJSONDoc(attribute="test_value")
        TestJSONDoc(attribute="test_value2")
        json_session.file_name = "data.json"
        json_session.commit()

        self.assertTrue(os.path.exists("data.json"))
        os.remove("data.json")

    def test_CVSDocument(self):

        doc = TestCSVDoc(d="test_value")
        print type(doc)
        TestCSVDoc(dddddddd="test_value2")
        csv_session.file_name = "data.csv"
        csv_session.commit()

        self.assertTrue(os.path.exists("data.csv"))
        os.remove("data.csv")

    def test_FileDocument(self):
        fileName='a.txt'

        TestFileDoc(fileName,'dhdbndnd')
        self.assertTrue(os.path.exists(fileName))