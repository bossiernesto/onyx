import contextlib


class FileDocument(object):
    def __init__(self, fileName, flags='r'):
        self.fileName = fileName
        self.flags = flags
        self.descriptor = self.getDescriptor(self.flags)

    @staticmethod
    def writeAndClose(fileName, rawData):
        file = FileDocument(fileName, 'w')
        with contextlib.closing(file.getDescriptor()) as f:
            f.write(rawData)

    def getDescriptor(self, flags=None):
        if not flags:
            flags = self.flags
        self.descriptor = open(self.fileName, flags)
        return self.descriptor

    @property
    def descriptor(self):
        return self._descriptor

    @descriptor.setter
    def descriptor(self, descriptor):
        self._descriptor = descriptor

    @descriptor.deleter
    def descriptor(self):
        self.commit()
        self._descriptor = None

    @property
    def fileName(self):
        return self._fileName

    @fileName.setter
    def fileName(self, fileName):
        self._fileName = fileName

    def commit(self):
        if self.descriptor:
            self.descriptor.flush()
            self.descriptor.close()

    def close(self):
        self.commit()