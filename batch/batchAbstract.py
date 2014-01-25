from .batchMetaclass import BatchMetaClass
from abc import abstractmethod
#TODO: Finish this module
from useful.common import logBeforeAfter
from config.AppContext import *

logger = getOnyxLogger()


class Batch(object):
    __metaclass__ = BatchMetaClass

    def __init__(self, appContext):
        self.appContext = appContext

    @abstractmethod
    def _do_action(self):
        raise NotImplementedError


