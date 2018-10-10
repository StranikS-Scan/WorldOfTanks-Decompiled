# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/web/storage.py


class IStorage(object):

    def close(self):
        raise NotImplementedError

    def add(self, name, data, callback):
        raise NotImplementedError

    def remove(self, name):
        raise NotImplementedError

    def isStored(self, name):
        raise NotImplementedError

    def getAll(self):
        raise NotImplementedError
