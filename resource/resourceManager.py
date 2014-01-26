import string
from abc import abstractmethod, ABCMeta
from resource import Request
from useful.common import retry, wrapException
from onyxexceptions import RequestException

#TODO: Finish this class up (add Validations,authentication)
class requestManager(object):
    """ The objective of this class is to manage all the higher level behaviour
	of a request and it's state """

    def __init__(self):
        """ Class attributes """
        self.retries = None
        self.delay = None
        self.settings = None
        self.requestHooks = list()

    def setRetries(self, retries):
        self.retries = retries

    def setDelay(self, delay):
        self.delay = delay

    def setSettings(self, settings):
        self.settings = settings

    def getDomain(self, url):
        if not (string.find(url, 'http')):
            return url.split('/', 3)[2]
        return url.split('/', 1)[0]

    #TODO: get retries from appContext
    @retry(RequestException, tries=3)
    def __get__request(self, url):
        response = None
        req = Request(self.settings)
        while response is None:
            try:
                response = req.getRequest(url, request_hooks=self.requestHooks)
            except Exception:
                #TODO: Create new Exception to reraise, check from status code if it's an HTPPError and see if some low level settings must be ajusted
                wrapException(RequestException, 'Request failed')
        return response

#Abstract class
class requestManagerBuilder(object):
    """ This is the builder class for the requestManagerClass """

    __metaclass__ = ABCMeta

    def __init__(self):
        """ Class initialiser """
        self.requestManager = None

    def getRequestManager(self):
        return self.requestManager

    def createRequestManager(self):
        self.requestManager = requestManager()

    @abstractmethod
    def buildDelay(self):
        raise NotImplementedError #this abstract method has to be defined in a concrete builder

    @abstractmethod
    def buildRetries(self):
        raise NotImplementedError #this abstract method has to be defined in a concrete builder

    @abstractmethod
    def buildSettings(self, settings):
        raise NotImplementedError #this abstract method has to be defined in a concrete builder

    @abstractmethod
    def buildRequestHooks(self, settings):
        raise NotImplementedError #this abstract method has to be defined in a concrete builder

#Default Concrete builder
class defaultRequestManager(requestManagerBuilder):
    """ This is the default concrete builder for the requestManager """

    DEFAULT_TRIES = 3
    DEFAULT_DELAY = 0

    def buildDelay(self):
        self.requestManager.setDelay(self.DEFAULT_DELAY)

    def buildRetries(self):
        self.requestManager.setRetries(self.DEFAULT_TRIES)

    def buildSettings(self, settings):
        self.requestManager.setSettings(settings)
