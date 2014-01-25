"""
.. module:: Onyx Spider Url Helper Class
   :platform: Linux
   :synopsis: Simple Observer Mixin
   :copyright: (c) 2011-2013 by Crawley Group.
   :license: BSD.

"""
from re import compile as re_compile
import urllib.parse
from html.extractors import XPathExtractor

#TODO: Build tests of this class
class UrlFinder():
    """
        This class will find for urls in htmls
    """
    _url_regex = re_compile(
        r'(http://|https://)([a-zA-Z0-9]+\.[a-zA-Z0-9\-]+|[a-zA-Z0-9\-]+)\.[a-zA-Z\.]{2,6}(/[a-zA-Z0-9\.\?=/#%&\+-]+|/|)')

    def __init__(self, response, search_hidden_urls=False):

        self.response = response
        self.search_hidden_urls = search_hidden_urls
        self.tree = XPathExtractor().get_object(self.response.raw)
        self.urls = self.get_urls()

    def get_urls(self):
        """Returns a list of urls found in the current html page"""
        urls = self.search_regulars()
        if self.search_hidden_urls:
            urls = self.search_hiddens(urls)
        return urls

    def search_regulars(self):
        """Search urls inside the <A> tags"""
        urls = set()
        for link_tag in self.tree.xpath("//a"):
            if not 'href' in link_tag.attrib:
                continue
            url = link_tag.attrib["href"]
            if not urllib.parse.urlparse(url).netloc:
                url = self._fix_url(url)
            url = self._normalize_url(url)
            urls.add(url)
        return urls

    def _fix_url(self, url):
        """Fix relative urls"""
        parsed_url = urllib.parse.urlparse(url)
        if not url.startswith("/"):
            url = "/%s" % url
        if parsed_url.scheme:
            url = "%s://%s%s" % (parsed_url.scheme, parsed_url.netloc, url)
        return url

    def _normalize_url(self, url):
        """Try to normalize some weird urls"""
        SLASHES = "//"
        if url.startswith(SLASHES):
            return url.replace(SLASHES, "http://")
        return url

    def search_hiddens(self, urls):
        """Search in the entire html via a regex"""
        for url_match in self._url_regex.finditer(self.response.raw):
            urls.add(url_match.group(0))
        return urls



