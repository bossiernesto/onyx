import urllib2
import urllib

class BaseRedirector():
    statusCode = ''
    redirections = []

    def clear_redirect_history(self):
        self.redirections = []

    def get_redirects(self):
        return self.redirections

class SmartRedirectHandler(urllib2.HTTPRedirectHandler,BaseRedirector):

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        newreq = urllib2.HTTPRedirectHandler.redirect_request(self,
                                                              req, fp, code, msg, headers, newurl)
        if newreq is not None:
            self.redirections.append((code, req.get_full_url()))
        return newreq

class NoRedirectionHandler(urllib2.HTTPRedirectHandler,BaseRedirector):

    def http_error_301(self, req, fp, code, msg, headers):
        infourl = urllib.addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl

    http_error_302 = http_error_301
    http_error_307 = http_error_301