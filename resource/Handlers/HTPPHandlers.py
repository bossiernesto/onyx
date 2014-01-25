import urllib2, urllib

class LogRedirectHandler(urllib2.HTTPRedirectHandler):

    #wrap http_error_300 in 302
    def http_error_302(self, req, fp, code, msg, headers):
        return super(LogRedirectHandler,self).http_error_302(req, fp, code, msg, headers)

    http_error_300 = http_error_307 = http_error_301 = http_error_303 = http_error_302

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        #Log Event
        return super(LogRedirectHandler,self).redirect_request(req, fp, code, msg, headers, newurl)

class NoRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        infourl = urllib.addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl
    http_error_300 = http_error_307 = http_error_301 = http_error_303 = http_error_302

