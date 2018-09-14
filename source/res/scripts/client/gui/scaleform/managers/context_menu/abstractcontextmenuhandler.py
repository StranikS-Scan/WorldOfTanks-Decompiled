# Embedded file name: scripts/client/gui/Scaleform/managers/context_menu/AbstractContextMenuHandler.py
from abc import ABCMeta, abstractmethod
import weakref
from Event import EventManager, Event
from debug_utils import LOG_WARNING
_SEPARATOR_ID = 'separate'

class AbstractContextMenuHandler(object):
    __metaclass__ = ABCMeta

    def __init__(self, cmProxy, ctx = None, handlers = None):
        self._eManager = EventManager()
        self.onContextMenuHide = Event(self._eManager)
        super(AbstractContextMenuHandler, self).__init__()
        self.__cmProxy = weakref.proxy(cmProxy)
        self.__handlers = handlers or {}
        self._initFlashValues(ctx)

    @property
    def app(self):
        return self.__cmProxy.app

    def fini(self):
        self._eManager.clear()
        self.__handlers = None
        self.__cmProxy = None
        self._clearFlashValues()
        return

    def getOptions(self, ctx = None):
        return self._generateOptions(ctx)

    def onOptionSelect(self, optionId):
        if optionId in self.__handlers:
            return getattr(self, self.__handlers[optionId])()
        LOG_WARNING('Unknown context menu option', self, self.__cmProxy, optionId)

    def _dispatchChanges(self, options):
        if self.__cmProxy is not None:
            self.__cmProxy._onOptionsChanged(options)
        return

    @classmethod
    def _makeItem(cls, optId, optLabel = None, optInitData = None, optSubMenu = None):
        return {'id': optId,
         'label': optLabel,
         'initData': optInitData,
         'submenu': optSubMenu}

    def _makeSeparator(self):
        return self._makeItem(_SEPARATOR_ID)

    @abstractmethod
    def _generateOptions(self, ctx = None):
        raise NotImplementedError

    def _initFlashValues(self, ctx):
        pass

    def _clearFlashValues(self):
        pass
