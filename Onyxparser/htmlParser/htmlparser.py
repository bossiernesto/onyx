"""
.. module:: Onyx HTML Parser based on lxml tree
   :platform: Linux
   :synopsis: HTML Parser that builds a collection of attributes based on the html
   :copyright: (c) 2012-2013 by Ernesto Bossi.
   :license: BSD.

.. moduleauthor:: Ernesto Bossi <bossi.ernestog@gmail.com>
"""
import onyxexceptions as ex

#TODO: make tests for this module
class HtmlParser():
    def __init__(self,response):
        if response.isFile:
            raise ex.HtmlParserException('Can\'t process a Non html response')
        self.brokenHTML=response.raw
        self.page=self.processRequest(self.brokenHTML)
        self.links=[] #consists of a list of tuples of (name,url)
        self.forms={}

    def processRequest(self,brokenhtml):
        pass #TODO: process the broken html

    def getLinks(self):
        if self.links is None:
            self.links=self.buildAnchors()

    def buildAnchors(self):
        pass

    def filrterLinksByName(self,expr):
        return [a_b for a_b in self.links if str.find(str(a_b[0]),expr)==-1]

    def filrterLinksByUrl(self,expr):
        return [a_b1 for a_b1 in self.links if str.find(str(a_b1[1]),expr)==-1]