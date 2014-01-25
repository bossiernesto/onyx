from abc import ABCMeta
import logging
from useful.common import getCurrentMethodName


class AbstractLogger(logging.Logger, metaclass=ABCMeta):
    def __init__(self, name):
        raise NotImplementedError


class DefaultLogger(AbstractLogger):
    """Default logger to build Decorator structure"""

    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.DEBUG)
        console = logging.StreamHandler()
        self.addHandler(console)


class DecoratorLogger(AbstractLogger):
    def __init__(self, name, loggers=[], loginstances=[]):
        self.loggers = []
        for log in loggers:
            inst = log()
            self.loggers.append(inst)
        for log in loginstances:
            self.loggers.append(log)
        logging.Logger.__init__(self, name, logging.DEBUG)


    def execLogger(self, func, msg, *args, **kwargs):
        for logger in self.loggers:
            getattr(logger, func)(msg, args, kwargs)

    #TODO: clean this to call only the inner method of this functions
    def critical(self, msg, *args, **kwargs):
        self.execLogger(getCurrentMethodName(), msg, args, kwargs)

    def error(self, msg, *args, **kwargs):
        self.execLogger(getCurrentMethodName(), msg, args, kwargs)

    def warning(self, msg, *args, **kwargs):
        self.execLogger(getCurrentMethodName(), msg, args, kwargs)

    def info(self, msg, *args, **kwargs):
        self.execLogger(getCurrentMethodName(), msg, args, kwargs)

    def debug(self, msg, *args, **kwargs):
        self.execLogger(getCurrentMethodName(), msg, args, kwargs)
