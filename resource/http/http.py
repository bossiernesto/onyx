import asyncio
import http.client

REPORT_HOOKS = "report_hooks"
CHUNK_HOOKS = "chunk_hooks"

class HttpOptions(object):
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

class HttpRequest(object):
    @asyncio.coroutine
    def request(self, method, params=None, data=None, options=None):



class BadStatusLine(Exception):
    pass

class ClientConnectionError(BadStatusLine):
    pass

class OSConnectionError(OSError):
    pass