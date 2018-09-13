# Embedded file name: scripts/client/gui/Scaleform/framework/entities/DisposableEntity.py
from Event import Event
from debug_utils import LOG_DEBUG
__author__ = 'd_trofimov'

class DisposableEntity(object):

    def __init__(self):
        super(DisposableEntity, self).__init__()
        self.onModuleDispose = Event()
        self.__created = False
        self.__disposed = False

    def create(self):
        self.__created = True
        self.__disposed = False
        self._populate()

    def destroy(self):
        if self.__disposed:
            return
        self.onModuleDispose(self)
        self.onModuleDispose.clear()
        self._dispose()
        self.__disposed = True

    def _populate(self):
        pass

    def _dispose(self):
        pass

    def _isCreated(self):
        return self.__created

    def isDisposed(self):
        return self.__disposed
