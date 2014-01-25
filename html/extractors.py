from abc import ABCMeta, abstractmethod
from lxml import etree
import io
from useful.common import isObjOfType


class AbstractExtractor(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_object(self, data):
        return data


class XPathExtractor(object):
    """
        Extractor using Xpath
    """

    def get_object(self, data):
        parser = etree.HTMLParser()
        memObj = io.StringIO if isObjOfType(data, str) else io.BytesIO
        html = etree.parse(memObj(data), parser)
        return html
