class OnyxException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class InvalidExtension(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class NotADirectory(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class HookException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class RequestException(IOError):
    def __init__(self, *args, **kwargs):
        IOError.__init__(self, *args, **kwargs)

class ConfigError(OnyxException):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class HtmlParserException(OnyxException):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class NotOfTypeException(OnyxException):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class LoggerException(OnyxException):
    def __init__(self,*args,**kwargs):
        OnyxException.__init__(self,*args,**kwargs)


#Testing Exceptions

class RetryableError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class AnotherRetryableError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class UnexpectedError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


#class Exceptions to pass
class DontManageException(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)