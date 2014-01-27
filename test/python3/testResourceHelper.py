from unittest import TestCase
from resource.resourceHelper import *
from collections import OrderedDict
from useful.common import isObjOfType
from urllib.parse import quote as quote2


def build_params(url, params):
    if isObjOfType(params, dict):
        return url + '&'.join(["%s=%s" % (k, v) for k, v in params.items()])


class TestResourceHelper(TestCase):
    def setUp(self):
        self.address_list = ['RECONQUISTA 151 , Capital Federal',
                             'AVENIDA CORRIENTES 3820 , Capital Federal',
                             'AVENIDA SANTA FE 1883 , Capital Federal',
                             'AVENIDA CABILDO 2412 , Capital Federal',
                             'Hortiguera 40, Capital Federal',
                             'Hortiguera 53, Capital Federal']
        self.encode_dirs = "%20to:".join([quote2(record) for record in self.address_list])
        self.arguments = OrderedDict(
            [('f', 'd'), ('hl', 'en'), ('saddr', self.encode_dirs), ('ie', 'UTF8&0'), ('om', '0'), ('output', 'html')])
        self.safe = "&%:"

    def test_url_encode(self):
        encodeToCheck = build_params('', self.arguments)
        self.assertEqual(encodeToCheck, ResourceHelper.urlencode(self.arguments, quote_via=quote2, safe=self.safe))

    def test_multiple_quoting(self):
        workingEncoding = "%20to:".join([quote2(record) for record in self.address_list])
        self.assertEqual(workingEncoding,
                         ResourceHelper.quote_collection(self.address_list, prefix=" to:", safe=self.safe,
                                                        quote_via=urllib.parse.quote))

    def test_single_encoding(self):
        self.assertEqual('foo=%2B%20', ResourceHelper.urlencode({"foo": "+ "}, quote_via=quote))

    def test_base_name(self):
        url = 'http://css3menu.com/download/css3menu-setup.zip?utm_source=free_downl_win&utm_medium=email&utm_campaign=css3_downl_link'
        self.assertEqual('css3menu-setup.zip', ResourceHelper.get_base_name(url))

    def test_pre_post_url(self):
        url = 'http://trade.nosis.com/Captcha?isHard=True&t=635018086580569985?captchaValue=AQY7C5'
        self.assertEqual(('http://trade.nosis.com/Captcha', 'isHard=True&t=635018086580569985?captchaValue=AQY7C5'),
                         ResourceHelper.get_pre_post_url(url))