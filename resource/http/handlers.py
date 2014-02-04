#Base handler class
class BaseHandler(object):
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_parent(self, parent_handler):
        self.parents.append(parent_handler)

    def close(self):
        for parent in self.parents:
            parent.close
        self.parents = []


class ProxyHandler(BaseHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.http = self.http
            self.accept_ssl = False
        except AttributeError:
            self.accept_ssl = True

    def get_schema(self):
        return self.https if self.accept_ssl else self.http


#Redirections
class BaseRedirector():
    statusCode = ''
    redirections = []

    def clear_redirect_history(self):
        self.redirections = []

    def get_redirects(self):
        return self.redirections


class HttpRedirectHandler(BaseHandler, BaseRedirector):
    def redirect_request(self):
        pass

    def on_code_301(self, request, code, message, headers):
        pass


class NoRedirectionHandler(HttpRedirectHandler, BaseRedirector):
    def on_code_301(self, request, code, message, headers):
        pass

    on_code_302 = on_code_301
    on_code_307 = on_code_301


class PreRequestHandler(object):
    pass


class PostRequestHandler(object):
    pass

class SanitizeHandler(PostRequestHandler):

    def after_request(self, response_request):
        from html import htmlsanitizer

        response_request.response_buffer = htmlsanitizer.sanitize_html(response_request.response_buffer)
        return response_request