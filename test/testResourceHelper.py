from unittest import TestCase
from resource.ResourceHelper import *
from ordereddict import OrderedDict
from useful.common import isObjOfType
import urllib

def buildParams(url,params):
    if isObjOfType(params,dict):
        return url+'&'.join(["%s=%s" % (k,v) for k,v in params.iteritems()])

class TestResourceHelper(TestCase):

    def setUp(self):
        self.address_list = ['RECONQUISTA 151 , Capital Federal',
                             'AVENIDA CORRIENTES 3820 , Capital Federal',
                             'AVENIDA SANTA FE 1883 , Capital Federal',
                             'AVENIDA CABILDO 2412 , Capital Federal',
                             'Hortiguera 40, Capital Federal',
                             'Hortiguera 53, Capital Federal']
        self.encode_dirs="%20to:".join([urllib.quote(record) for record in self.address_list])
        self.arguments=OrderedDict([('f','d'), ('hl','en'),('saddr',self.encode_dirs),('ie','UTF8&0'),('om','0'),('output','html')])
        self.safe="&%:"

    def testUrlEncode(self):
        encodeToCheck=buildParams('',self.arguments)
        self.assertEqual(encodeToCheck,ResourceHelper.urlencode(self.arguments,quote_via=urllib.quote,safe=self.safe))

    def testMultipleQuoting(self):
        workingEncoding="%20to:".join([urllib.quote(record) for record in self.address_list])
        self.assertEqual(workingEncoding,ResourceHelper.quoteCollection(self.address_list,prefix=" to:",safe=self.safe,quote_via=urllib.quote))

