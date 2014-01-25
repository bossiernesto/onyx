from config.AppContext import appContext,ONYX_ROOT
from config.AppContext import MASTER_CATALOG,DOCUMENTAL_DB
from onyxexceptions import ConfigError

documents_entities = []
DEFAULT_FILE='DocumentalFile'
appC=appContext.getInstance()

class DocumentMeta(type):
    """
        This metaclass adds the user's documents storages to a list
        used by the CLI commands.
        Abstract base documents storages won't be added.
    """

    def __init__(cls, name, bases, dct):
        if not hasattr(cls, '__module__' ) or not cls.__module__.startswith(ONYX_ROOT):
            documents_entities.append(cls)
        super(DocumentMeta, cls).__init__(name, bases, dct)


class BaseDocumentSession(object):

    def set_up(self,storage_name):
        section=self.get_section(appContext().getInstance()) #Retrieve section from master catalog
        try:
            self.file_name = appContext().getInstance().get_value(section,storage_name)
        except ConfigError: #if the storage name is not set
            self.file_name = DEFAULT_FILE
            appContext().getInstance().set_property(section,storage_name,self.file_name)

    def get_section(self,appC):
       return appC.get(MASTER_CATALOG,DOCUMENTAL_DB)

    def remove(self):
        appContext().getInstance().remove(self.get_section(appC),self)

    def close(self):
        pass