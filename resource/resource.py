"""
.. module:: Onyx request Module
   :platform: Linux
   :synopsis: urllib2 Wrapper on steroids
   :copyright: (c) 2012-2013 by Ernesto Bossi.
   :license: BSD.

.. moduleauthor:: Ernesto Bossi <bossi.ernestog@gmail.com>
"""
import urllib2, contextlib
import onyxexceptions as ex
from abc import ABCMeta, abstractmethod
from cookie import cookiejar
from hooks.hooks import chunk_report, sanitizeHtml
from useful.observableMixin import *
from useful.common import wrap_exception, buffer_optimal_size, report_run, format_block, toKB, fixZeroResult, time_now, delay
from ResourceHelper import *
from RequestStatistics import RequestStatistics
from Handlers.SmartRedirectorHandler import SmartRedirectHandler, NoRedirectionHandler
from RequestDynamicBehaviour import injectBehaviour

#Configuration of Request (Low level configuration)
#TODO: Dissasociate different auth tokens (NTLM,Kerberos)

REPORT_HOOKS = "report_hooks"
CHUNK_HOOKS = "chunk_hooks"


class request_settings(object):
    def __init__(self, cookiej=None, chunk_hooks=[chunk_report], statistics=False, redirects=True):
        self.handlers = [urllib2.HTTPHandler(), urllib2.HTTPSHandler()]
        self.headers = {}
        self.hooks = {CHUNK_HOOKS: chunk_hooks}
        self.hooks[REPORT_HOOKS] = []
        self.statistics = RequestStatistics.getInstance() if statistics else None
        if cookiej is None:
            #Set CookieJar
            self.cj = cookiejar.OnyxCookieJar()
        else:
            self.cj = cookiej
        self.handlers.append(self.cj)
        self.redirector = SmartRedirectHandler() if redirects else NoRedirectionHandler()
        self.setRedirectorHandler(self.redirector)

    def setHandler(self, handler):
        self.handlers.append(handler)

    #Hooks
    def getReportHooks(self):
        return self.getHook(REPORT_HOOKS)

    def getChunkHooks(self):
        return self.getHook(CHUNK_HOOKS)

    def getHook(self, name):
        try:
            return self.hooks[name]
        except KeyError:
            return []

    def getCookieHandler(self):
        """CookeHandler getter"""
        return self.cj

    #Sets Proxy Handler to connector
    def setProxyHandler(self, user, password, proxy='', port='80'):
        """Proxy hanlder settings, in the next milestone it should take the parameters from the global settings"""
        handler = 'http://%s:%s@%s:%s' % (user, password, proxy, port)
        self.handlers.append(urllib2.ProxyHandler({'http': handler, 'https': handler}))

    #Sets RedirectHandlertoConnector
    def setRedirectorHandler(self, handler=SmartRedirectHandler()):
        """Redirector Handler, as a default value it used the urllib2 one, but it's recommended to use the SnartRedirecthandler,
        as it's a wrapper handler that logs all redirections to the program logger"""
        handler.clear_redirect_history()
        self.handlers.append(handler)

    def setSafeHtml(self):
        self.hooks[CHUNK_HOOKS].append(sanitizeHtml)

    def setRedirects(self, request):
        handler = self.getHandler(urllib2.HTTPRedirectHandler)
        if isinstance(handler,
                      SmartRedirectHandler): #if redirect handler is a HTTPRedirectHandler it doesn/'t store history
            request.addHistory(handler.get_redirects())

    def getHandler(self, klass):
        for handler in self.handlers:
            if isinstance(handler, klass):
                return handler

    #Sets of headers
    def setAgent(self, agent='Mozilla/5.0'):
        """Set Agent Description. This option is useful as it's fundamental to the spider not to make requests
        and get identified as a Python program"""
        self.headers['User-agent'] = agent

    def setCharset(self, charset="ISO-8859-1,utf-8;q=0.7,*;q=0.3"):
        """Set Charset, default value is ISO-8859"""
        self.headers["Accept-Charset"] = charset

    def setStatistics(self):
        self.statistics = RequestStatistics.getInstance()

    def setReferer(self, ref):
        """Set referer header"""
        self.headers["Referer"] = ref


    def buildOpenerWrapper(self, func, args):
        """Partial helper function"""
        return func(*args)

    def buildOpener(self):
        """This method is responsible for installing all the handlers/headers that have been set to the opener, and that
        will be used by the request"""
        opener = self.buildOpenerWrapper(urllib2.build_opener, self.handlers)
        self.installHeaders(opener)
        urllib2.install_opener(opener)
        return opener

    def installHeaders(self, opener):
        #iterate over headers and add them to the opener
        for header, value in self.headers.iteritems():
            opener.addheaders = [(header, value)]


class Request(object, Subject):
    """Main request class. This class does all the low level work for POST/GET requests and is responsible for cleaning
    the request, url and adjust it's behaviour by the settings that was given"""

    def __init__(self, settings):
        if settings is None:
            self.settings = request_settings()
            self.settings.setAgent() #set Spider Agent as Mozilla and not like Python 2.7
            self.settings.setCharSet()
        else:
            self.settings = settings
        self.initVariables()
        Subject.__init__(self)
        self.attach(self.settings.statistics)

    @property
    def html(self):
        return self._html

    @html.setter
    def html(self, html):
        self._html = html

    @property
    def raw(self):
        return self._raw

    @raw.setter
    def raw(self, raw):
        self._raw = raw

    def initVariables(self):
        self.cleanHistory()
        self.url = None
        self.raw = None
        self.html = None
        self.redirections = 0
        self._action = requestDefault()
        self.isFile = False

    def cleanHistory(self):
        self.history = []

    def addHistory(self, history):
        self.history += history

    def getSettings(self):
        return self.settings

    #setter/getter for strategy _action_get
    def _action_set(self, method):
        """Strategy setter for _action_get"""
        if isinstance(method, requestHTML):
            self._action = method

    def _action_get(self):
        """Strategy getter for _action_get"""
        return self._action

    def postRequest(self, url, values, headers=dict(), processValues=True, request_hooks=list()):
        """PostRequest, it'll do a POST with values passed by parameter, function encodes the values, so they should be
        passed as a list"""
        parameters = ResourceHelper.urlencode(values, quote_via=quote) if processValues == True else values
        if headers: #Build custom headers
            req = urllib2.Request(ResourceHelper.normalizeUrl(url), data=parameters, headers=headers)
            self.getRequest(req, None, request_hooks)
            return
        req = urllib2.Request(ResourceHelper.normalizeUrl(url) + '?' + parameters) #try to fix this
        self.getRequest(req, None, request_hooks)

    def preProcess(self, url, parameters, opener):
        if not isinstance(url, urllib2.Request):
            self.url = ResourceHelper.normalizeUrl(url)
            return opener.open(self.url, data=parameters)
        else:
            return opener.open(url)


    def reportRuntime(self, runtime):
        runtime = fixZeroResult(runtime)
        self.speed = toKB(self.total_size / runtime)

    #@benchmark # for debug purposes
    @report_run
    @notify
    def getRequest(self, url, parameters=None, request_hooks=list()):
        """Main GetRequest action to get the contents of a url. Can attack a hook per request and selects an action
        depending if it's an html/json/xml or a file"""
        self.initVariables()
        opener = self.settings.buildOpener()
        try:
            with contextlib.closing(self.preProcess(url, parameters, opener)) as response:
                if response is None: raise AttributeError
                self.setRequestData(response)
                self.analizeRequest()
                responseBuffer = self.read_chunks(response, self.chunkSize,
                                                  self.settings.getChunkHooks()) # read response
                self._action_get().actionRequest(responseBuffer, self, self.settings.getReportHooks())
            return self.raw
        except urllib2.HTTPError, e:
            #catch any low level Exception and retrow it
            self.status_code = e.code
            self.notifyValues(status_code=self.status_code, timestamp=time_now()) #notificate
            wrap_exception(ex.RequestException,
                          "Exception with request {0} error code {1}, reason {2}".format(self, e.code, e.reason))

    def setRequestData(self, request):
        self.info = request.info()
        self.status_code = request.getcode()
        self.response = request
        if self.url != request.url: #Redirection detected
            self.url = request.url
            self.settings.setRedirects(self)
        self.history.append((self.status_code, self.url))
        self.redirections = len(self.history) - 1
        injectBehaviour(self)

    #Function to analize the request
    def analizeRequest(self):
        """Analize if request is actually a file, in case it's set the action to persist it to the document session"""
        #Check if it's a file
        content = self.info.getheader('Content-Length')
        self.total_size = 0 if content is None else int(content.strip())
        self.chunkSize = buffer_optimal_size(self.total_size)
        if not ResourceHelper.is_readable(self.info):
            self.isFile = True
            self._action_set(requestFile())

    #Functions for Request processing to broken html
    #@benchmark # for debug purposes
    def read_chunks(self, response, chunk_size=8192, chunk_hooks=list()):
        """Function to read and process the response.
        This function comes with a hook similar to urllib getRequest() function"""
        bytes_so_far = 0
        data = []

        while 1:
            chunk = response.read(chunk_size)
            bytes_so_far += len(chunk)

            if not chunk:
                break

            data += chunk
            if chunk_hooks:
                if self.total_size < bytes_so_far: self.total_size = bytes_so_far
                try:
                    for hook in chunk_hooks:
                        hook(bytes_so_far, chunk_size, self.total_size)
                except Exception:
                    raise wrap_exception(ex.HookException(), "Problem with hook {0}".format(hook))
            #if self.settings.statistics is not None:
        #    RequestStatistics.getInstance().updateTransmited(bytes_so_far)
        return "".join(data)

    def getRequestDebug(self):

        requestResumee = '''
                       ############### Request Debug ################
                       Url fetched= {0}
                       Size downloaded = {1} Kb
                       Average Speed = {2} Kbs/sec
                       Status code = {3}
                       Is a File = {4}

                       ###############     HEADERS   ################

                       {5}

                       '''.format(self.url, "%.2f" % (self.total_size / 1024), "%.2f" % self.speed, self.status_code,
                                  self.isFile, self.info)
        if self.redirections > 0:
            requestResumee += '''
                        ############ Redirections History ############

                        Redirection Count = {0}

                        {1}

                        '''.format(self.redirections, self.history)

        return format_block(requestResumee)


class requestHTML(object):
    """Abstract class to actionRequest Strategy. This strategy is used to do an action based on the GET/POST request"""
    __metaclass__ = ABCMeta

    def actionRequest(self, responseBuffer, response, request_hooks):
        if request_hooks:
            for hook in request_hooks:
                try:
                    hook(responseBuffer, response)
                except ex.HookException:
                    raise wrap_exception(ex.HookException(), "Problem with hook {0}".format(hook))
        self._actionRequest(responseBuffer, response)

    @abstractmethod
    def _actionRequest(self, responseBuffer, request):
        #abstract method
        raise NotImplementedError


class requestDefault(requestHTML):
    def _actionRequest(self, responseBuffer, request):
        #report the status of the response and get the broken html
        """This is the Default action for a request and is used when the response is generally a content like
        HTML"""
        request.html(responseBuffer)
        request.raw(responseBuffer)


class requestFile(requestHTML):
    """RequestFile is a concrete action, where the file or flow is persisted to the Document Session, if there isn't
    an open session, it should invoke and open one."""

    def _actionRequest(self, responseBuffer, request):
        #save file from buffer and log it before to send it to the container
        from persistance.documents import FileDocument

        request.fileName = ResourceHelper.get_base_name(request.url)
        FileDocument.writeAndClose(request.fileName, responseBuffer)
        request.raw(responseBuffer)


class DelayedRequest(Request):
    def __init__(self, settings, Indelay=0, deviation=0):
        Request.__init__(self, settings)
        self.delay = Indelay
        self.deviation = deviation
        self.getRequest = delay(delayFactor=1, Mindelay=self.delay, Indeviation=self.deviation)(self.getRequest)
        self.postRequest = delay(delayFactor=1, Mindelay=self.delay, Indeviation=self.deviation)(self.postRequest)

    def getRequest(self, url, parameters=None, request_hooks=list()):
        return super(DelayedRequest, self).getRequest(url, parameters, request_hooks)

    def postRequest(self, url, values, headers=dict(), processValues=True, request_hooks=list()):
        return super(DelayedRequest, self).postRequest(url, values, headers, processValues, request_hooks)
