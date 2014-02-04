import urllib.parse
import functools
import asyncio
import http.client
import http.cookiejar
from resource.RequestStatistics import RequestStatistics
from .handlers import *
from hooks.hooks import chunk_report

REPORT_HOOKS = "report_hooks"
CHUNK_HOOKS = "chunk_hooks"

ACCEPTED_VERSIONS = [(1, 0), (1, 1)]

#Methods Constants
POST_METHODS = []
REQUEST_METHODS = []
VALID_METHODS = POST_METHODS + REQUEST_METHODS


def version_to_str(version_tuple):
    return 'HTTP/{0}.{1}'.format(version_tuple)


class HttpOptions(object):
    def __init__(self, chunk_hooks=[chunk_report], statistics=False, allow_redirects=True, max_redirections=5,
                 version=None, encoding='utf-8', loop=None, auth=None, timeout=None, compress=None, verify_ssl=True,
                 session=None, check_robots=True):
        self.handlers = []
        self.headers = {}
        self.version = version or (1, 1)
        self.hooks = {CHUNK_HOOKS: chunk_hooks}
        self.hooks[REPORT_HOOKS] = []
        self.statistics = self.setStatistics() if statistics else None
        self.event_loop = loop or asyncio.get_event_loop()
        self.check_robots = True

        #redirects
        self.allow_redirects = allow_redirects
        self.max_redirections = max_redirections
        self.redirector = HttpRedirectHandler() if allow_redirects else NoRedirectionHandler()
        self.setRedirectorHandler(self.redirector)

        #other options
        self.timeout = timeout or 100 #default 100 milliseconds
        self.compress = compress
        self.verify_ssl = verify_ssl

        #session
        self.session = session
        self.auth = auth


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

    #Sets Proxy Handler to connector
    def setProxyHandler(self, user, password, proxy='', port='80', domains=['http', 'https']):
        """Proxy hanlder settings, in the next milestone it should take the parameters from the global settings"""
        handler = 'http://%s:%s@%s:%s' % (user, password, proxy, port)
        for domain in domains:
            self.handlers.append(ProxyHandler({domain: handler}))


    #Sets RedirectHandlertoConnector
    def setRedirectorHandler(self, handler=HttpRedirectHandler()):
        handler.clear_redirect_history()
        self.handlers.append(handler)

    def setSafeHtml(self):
        self.handlers.append(SanitizeHandler)

    def setRedirects(self, request):
        handler = self.getHandler(HttpRedirectHandler)
        #if redirect handler is a HTTPRedirectHandler it doesn/'t store history
        if handler:
            request.addHistory(handler.get_redirects())

    def getHandler(self, klass):
        for handler in self.handlers:
            if isinstance(handler, klass):
                return handler
        return None

    #Sets of headers
    def setAgent(self, agent='Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'):
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


class DefaultHTTPOptions(HttpOptions):
    def __init__(self, chunk_hooks=[chunk_report], statistics=False, allow_redirects=True):
        self.setAgent()
        self.setCharset()
        #TODO: Uncomment when session is done
        #self.session = OnyxSession

    @classmethod
    def build(cls):
        return DefaultHTTPOptions()


@asyncio.coroutine
def _do_connection(request, event_loop, connection_params):
    if connection_params is not None:
        transport, proto = yield from event_loop.create_connection(
            functools.partial(StreamProtocol, loop=event_loop),
            connection_params['host'], connection_params['port'],
            ssl=connection_params['ssl'], family=connection_params['family'],
            proto=connection_params['proto'], flags=connection_params['flags'])
    else:
        transport, proto = yield from event_loop.create_connection(
            functools.partial(StreamProtocol, loop=event_loop),
            request.host, request.port, ssl=request.ssl)
    wrp = TransportWrapper(transport)
    return transport, proto, wrp

@asyncio.coroutine
def request(self, method, url, params=None, data=None, options=None, compress=None,
            connection_params=None, cookies=None, files=None):
    """Builds a request with the specified parameters defined on the settings and on the args."""
    options = options or DefaultHTTPOptions.build()
    redirects = 0

    while True:
        request = HTTPRequest(method, url, options, params=params, data=data, compress=compress,
                              connection_params=connection_params,
                              cookies=cookies, files=files)
        connector = _do_connection if options.session else options.session
        connection = connector(request, options.event_loop, connection_params)
        timeout = options.timeout
        connection_task = asyncio.async(connection, loop=options.event_loop)

        try:
            if timeout:
                transport, proto, wrp = yield from asyncio.wait_for(connection_task, timeout, loop=options.event_loop)
            else:
                transport, proto, wrp = yield from connection_task

                resp = yield from _make_request(
                    transport, proto, request, wrp, timeout, options.event_loop)
        except asyncio.TimeoutError:
            raise TimeoutError from None
        except BadStatusLine as exc:
            raise ClientConnectionError(exc)
        except OSError as exc:
            raise OSConnectionError(exc)
        finally:
            connection_task.cancel()
         # redirects
        if resp.status in (301, 302) and options.allow_redirects:
            redirects += 1
            if options.max_redirects and redirects >= options.max_redirects:
                resp.close()
                break

            r_url = resp.get('location') or resp.get('uri')

            scheme = urllib.parse.urlsplit(r_url)[0]
            if scheme not in ('http', 'https', ''):
                raise ValueError('Can redirect only to http or https')
            elif not scheme:
                r_url = urllib.parse.urljoin(url, r_url)

            url = urllib.parse.urldefrag(r_url)[0]
            if url:
                resp.close()
                continue

        break

    return resp

class HTTPResponse(object):
    pass


class HTTPRequest(object):
    def __init__(self, method, url, options, params=None, data=None, compress=None, connection_params=None,
                 cookies=None, files=None):
        self.validate_method(method)

    def validate_method(self, method):
        if method not in VALID_METHODS:
            raise OnyxHTTPException("{0} is not a valid method".format(method))


class BadStatusLine(Exception):
    pass


class ClientConnectionError(BadStatusLine):
    pass


class OSConnectionError(OSError):
    pass


class OnyxHTTPException(Exception):
    pass