from useful.singleton import Singleton
import urllib2
import sys
from urllib import *

try:
    unicode
except NameError:
    def _is_unicode(x):
        return 0
else:
    def _is_unicode(x):
        return isinstance(x, unicode)

HTTP_BEGIN = "http://"
HHTPS_BEGIN = "https://"

TYPE_HTML = 'text/html'
TYPE_XML = 'text/xml'
TYPE_JSON = 'application/json'
TYPE_ZIP = 'application/zip'
TYPE_JPG = 'image/jpeg'
TYPE_PNG = 'image/png'

class ResourceHelper(Singleton):

    @staticmethod
    def prepareUrl(url):
        pass

    @staticmethod
    def isReadable(info):
        readable = [TYPE_HTML,TYPE_XML,TYPE_JSON]
        try:
            for r in readable:
                if info['content-type'].startswith(r):
                    return True
            return False
        except KeyError:
            return True

    @staticmethod
    def checkPrefix(url):
        if not url.startswith(HTTP_BEGIN) and not url.startswith(HHTPS_BEGIN):
            return 'http://'+url
        return url

    @staticmethod
    def normalizeUrl(url):
        """Normalize URL and clean it"""
        urlNew=ResourceHelper.checkPrefix(url)
        return urllib2.quote(urlNew.encode('utf-8'), safe="%/:=&?~#+!$,;'@()*[]")

    @staticmethod
    def quoteCollection(collection,prefix='',quote_via=quote_plus,safe="/"):
        if isinstance(collection,list):
            return quote_via(prefix.join([element for element in collection]),safe=safe)

    @staticmethod
    def urlencode(query, doseq=0,quote_via=quote_plus,safe="/~#!$,;'@()*[]"):
        """Encode a sequence of two-element tuples or dictionary into a URL query string.

        If any values in the query arg are sequences and doseq is true, each
        sequence element is converted to a separate parameter.

        If the query arg is a sequence of two-element tuples, the order of the
        parameters in the output will match the order of parameters in the
        input.
        """
        if hasattr(query,"items"):
            # mapping objects
            query = query.items()
        else:
            # it's a bother at times that strings and string-like objects are
            # sequences...
            try:
                # non-sequence items should not work with len()
                # non-empty strings will fail this
                if len(query) and not isinstance(query[0], tuple):
                    raise TypeError
                    # zero-length sequences of all types will get here and succeed,
                    # but that's a minor nit - since the original implementation
                    # allowed empty dicts that type of behavior probably should be
                    # preserved for consistency
            except TypeError:
                ty,va,tb = sys.exc_info()
                raise TypeError, "not a valid non-string sequence or mapping object", tb

        l = []
        if not doseq:
            # preserve old behavior
            for k, v in query:
                k = quote_via(str(k),safe)
                v = quote_via(str(v),safe)
                l.append(k + '=' + v)
        else:
            for k, v in query:
                k = quote_via(str(k))
                if isinstance(v, str):
                    v = quote_via(v)
                    l.append(k + '=' + v)
                elif _is_unicode(v):
                    # is there a reasonable way to convert to ASCII?
                    # encode generates a string, but "replace" or "ignore"
                    # lose information and "strict" can raise UnicodeError
                    v = quote_via(v.encode("ASCII","replace"),safe)
                    l.append(k + '=' + v)
                else:
                    try:
                        # is this a sufficient test for sequence-ness?
                        len(v)
                    except TypeError:
                        # not a sequence
                        v = quote_via(str(v),safe)
                        l.append(k + '=' + v)
                    else:
                        # loop over the sequence
                        for elt in v:
                            l.append(k + '=' + quote_via(str(elt),safe))
        return '&'.join(l)

    @staticmethod
    def getBaseName(url):
        filename, file_ext= ResourceHelper.getFileAndExt(url)
        return filename+file_ext

    @staticmethod
    def getFileAndExt(url):
        from urlparse import urlparse
        from os.path import splitext, basename

        disassembled = urlparse(url)
        return splitext(basename(disassembled.path))

    @staticmethod
    def getPrePostUrl(url):
        return url.split('?')[0],'?'.join(url.split('?')[1:])

if __name__ == '__main__':

    print ResourceHelper.urlencode({"foo": "+ "},quote_via=quote)
    a='http://css3menu.com/download/css3menu-setup.zip?utm_source=free_downl_win&utm_medium=email&utm_campaign=css3_downl_link'
    print ResourceHelper.getBaseName(a)
    b='http://trade.nosis.com/Captcha?isHard=True&t=635018086580569985?captchaValue=AQY7C5'
    print ResourceHelper.getPrePostUrl(b)

