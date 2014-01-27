#TODO: finish this module
import pickle
from persistance.documents.file_doc import FileDocument
from useful.common import wrap_exception
from onyxexceptions import OnyxException, NotOfTypeException

import weakref


class MetaPickleable(type):
    def __init__(cls, name, bases, dct):
        super(MetaPickleable, cls).__init__(cls, name, bases, dct)
        if 'fileName' in dct:
            filename = cls.fileName
        else:
            filename = cls.generateID(cls.__name__)
        cls._pickleJar = FileDocument(filename, 'w')
        cls.fileName = filename
        cls.__instance_refs__ = []

    def generateID(cls, name):
        return 'Jar_' + name + '.obj'

    def __instances__(cls):
        instances = []
        validrefs = []
        for ref in cls.__instance_refs__:
            instance = ref()
            if instance is not None:
                instances.append(instance)
                validrefs.append(ref)
        cls.__instance_refs__ = validrefs
        return instances


class Pickeable():
    __metaclass__ = MetaPickleable

    def __new__(*args, **kwargs):
        cls = args[0]
        self = super(MetaPickleable, cls).__new__(cls)
        cls.__instance_refs__.append(weakref.ref(self))
        return self

    def __reduce_ex__(self, proto):
        return super(Pickeable, self).__reduce_ex__(2)

    @property
    def pickleJar(self):
        return self._pickleJar

    @pickleJar.setter
    def pickleJar(self, jar):
        self._pickleJar = jar

    def checkType(self, obj):
        if self.type is None:
            self.type = type(obj)
        if not isinstance(obj, self.type):
            raise NotOfTypeException('object {0} is should be of instance {1}'.format(obj, self.type))

    def serializeObject(self, obj):
        try:
            self.checkType(obj)
            self.objs.add(obj)
            FileDocument.writeAndClose(self.filename, self.objs)
        except (IOError, NotOfTypeException) as e:
            wrap_exception(OnyxException, 'Raised an exception of type {0}'.format(e))

    def getObjects(self):
        descriptor = self.pickleJar.getDescriptor()
        objs = pickle.load(descriptor)
        del descriptor
        return objs


if __name__ == '__name__':
    pass