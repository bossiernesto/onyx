from useful.singleton import Singleton
import urllib.error
import sys
from urllib.parse import quote_plus, quote

try:
    str
except NameError:
    def _is_unicode(x):
        return 0
else:
    def _is_unicode(x):
        return isinstance(x, str)

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
    def is_readable(info):
        readable = [TYPE_HTML, TYPE_XML, TYPE_JSON]
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
            return 'http://' + url
        return url

    @staticmethod
    def normalizeUrl(url):
        """Normalize URL and clean it"""
        urlNew = ResourceHelper.checkPrefix(url)
        return urllib.parse.quote(urlNew.encode('utf-8'), safe="%/:=&?~#+!$,;'@()*[]")

    @staticmethod
    def quote_collection(collection, prefix='', quote_via=quote_plus, safe="/"):
        """
        Quote for collection of resources of urls.
        """
        if isinstance(collection, list):
            return quote_via(prefix.join([element for element in collection]), safe=safe)

    @staticmethod
    def urlencode(query, doseq=0, quote_via=quote_plus, safe="/~#!$,;'@()*[]"):
        """Encode a sequence of two-element tuples or dictionary into a URL query string.

        If any values in the query arg are sequences and doseq is true, each
        sequence element is converted to a separate parameter.

        If the query arg is a sequence of two-element tuples, the order of the
        parameters in the output will match the order of parameters in the
        input.
        """
        if hasattr(query, "items"):
            # mapping objects
            query = list(query.items())
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
                ty, va, tb = sys.exc_info()
                raise TypeError("not a valid non-string sequence or mapping object").with_traceback(tb)

        l = []
        if not doseq:
            # preserve old behavior
            for k, v in query:
                k = quote_via(str(k), safe)
                v = quote_via(str(v), safe)
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
                    v = quote_via(v.encode("ASCII", "replace"), safe)
                    l.append(k + '=' + v)
                else:
                    try:
                        # is this a sufficient test for sequence-ness?
                        len(v)
                    except TypeError:
                        # not a sequence
                        v = quote_via(str(v), safe)
                        l.append(k + '=' + v)
                    else:
                        # loop over the sequence
                        for elt in v:
                            l.append(k + '=' + quote_via(str(elt), safe))
        return '&'.join(l)

    @staticmethod
    def get_base_name(url):
        """
        Get base of the url.
        """
        filename, file_ext = ResourceHelper.get_file_and_ext(url)
        return filename + file_ext

    @staticmethod
    def get_file_and_ext(url):
        from urllib.parse import urlparse
        from os.path import splitext, basename

        disassembled = urlparse(url)
        return splitext(basename(disassembled.path))

    @staticmethod
    def get_pre_post_url(url):
        """
        separate url base from the parameters that form part of the post data.
        """
        return url.split('?')[0], '?'.join(url.split('?')[1:])

    @staticmethod
    def get_domain(url):
        parsed_uri = urllib.parse.urlparse(url)
        return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)