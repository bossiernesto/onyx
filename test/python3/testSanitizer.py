import doctest
from html.htmlsanitizer import SafeHTMLStr, SafeHTMLUnicode
from unittest import TestCase


class TestHTMLSanitizerStr(TestCase):
    def test_testdoc(self):
        doctest.testmod(SafeHTMLStr)
        doctest.testmod(SafeHTMLUnicode)

