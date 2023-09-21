# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/managers/context_menu.py
import inspect
import weakref
from abc import ABCMeta, abstractmethod
import Keys
from Event import EventManager, Event
from debug_utils import LOG_WARNING
from gui import InputHandler
from gui.Scaleform.daapi.view.bootcamp.component_override import BootcampComponentOverride
from gui.Scaleform.framework.entities.abstract.ContextMenuManagerMeta import ContextMenuManagerMeta
from soft_exception import SoftException
CM_BUY_COLOR = 13347959
_SEPARATOR_ID = 'separate'
_handlers = {}

def registerHandlers(*handlers):
    handlerTypes = []
    for item in handlers:
        if len(item) < 2:
            raise SoftException('Item {} is invalid'.format(item))
        handlerType, handler = item[:2]
        if handlerType in _handlers:
            raise SoftException('Type of handler {} already exists'.format(handlerType))
        if isinstance(handler, BootcampComponentOverride):
            handler = handler()
        if not inspect.isclass(handler) or AbstractContextMenuHandler not in inspect.getmro(handler):
            raise SoftException('Handler {} is invalid'.format(handler))
        _handlers[handlerType] = handler
        handlerTypes.append(handlerType)

    return handlerTypes


def unregisterHandlers(*handlerTypes):
    for handlerType in handlerTypes:
        _handlers.pop(handlerType, None)

    return


def _getHandlerClass(handlerType):
    if handlerType in _handlers:
        return _handlers[handlerType]
    else:
        LOG_WARNING('Unknown context menu handler type', handlerType)
        return None


class ContextMenuManager(ContextMenuManagerMeta):

    def __init__(self, app):
        super(ContextMenuManager, self).__init__()
        self.setEnvironment(app)
        self.onContextMenuHide = Event()
        self.__currentHandler = None
        return

    def getCurrentHandler(self):
        return self.__currentHandler

    def pyHide(self):
        self.as_hideS()

    def show(self, menuType, args):
        self.as_showS(menuType, args)

    def requestOptions(self, handlerType, ctx):
        clazz = _getHandlerClass(handlerType)
        if clazz is not None:
            self.__currentHandler = clazz(self, ctx)
            self.__currentHandler.onContextMenuHide += self.as_hideS
            InputHandler.g_instance.onKeyDown += self.__onKeyDown
            self._sendOptionsToFlash(self.__currentHandler.getOptions(ctx))
        return

    def onOptionSelect(self, optionId):
        if self.__currentHandler is not None:
            self.__currentHandler.onOptionSelect(optionId)
        return

    def onHide(self):
        if self.__isMenuActive():
            self.onContextMenuHide()
        self.__disposeHandler()

    def _dispose(self):
        self.__app = None
        self.__disposeHandler()
        super(ContextMenuManager, self)._dispose()
        return

    def _sendOptionsToFlash(self, options):
        self.as_setOptionsS({'options': options})

    def _onOptionsChanged(self, options):
        self._sendOptionsToFlash(options)

    def __disposeHandler(self):
        InputHandler.g_instance.onKeyDown -= self.__onKeyDown
        if self.__currentHandler is not None:
            self.__currentHandler.onContextMenuHide -= self.as_hideS
            self.__currentHandler.fini()
            self.__currentHandler = None
        return

    def __onKeyDown(self, event):
        if event.key == Keys.KEY_ESCAPE:
            self.pyHide()

    def __isMenuActive(self):
        return self.__currentHandler is not None


class AbstractContextMenuHandler(object):
    __metaclass__ = ABCMeta

    def __init__(self, cmProxy, ctx=None, handlers=None):
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

    def getOptions(self, ctx=None):
        return self._generateOptions(ctx)

    def onOptionSelect(self, optionId):
        if optionId in self.__handlers:
            return getattr(self, self.__handlers[optionId])()
        LOG_WARNING('Unknown context menu option', self, self.__cmProxy, optionId)

    def getCMInfo(self):
        pass

    def _dispatchChanges(self, options):
        if self.__cmProxy is not None:
            self.__cmProxy._onOptionsChanged(options)
        return

    @classmethod
    def _makeItem(cls, optId, optLabel=None, optInitData=None, optSubMenu=None, linkage=None, iconType=''):
        return {'id': optId,
         'label': optLabel,
         'iconType': iconType,
         'initData': cls.__makeOptDataDefaults(optInitData),
         'submenu': optSubMenu,
         'linkage': linkage}

    def _makeSeparator(self):
        return self._makeItem(_SEPARATOR_ID)

    @abstractmethod
    def _generateOptions(self, ctx=None):
        raise NotImplementedError

    def _initFlashValues(self, ctx):
        pass

    def _clearFlashValues(self):
        pass

    @staticmethod
    def __makeOptDataDefaults(optInitData):
        if optInitData is None:
            return {'visible': True}
        else:
            if 'visible' not in optInitData or optInitData['visible'] is None:
                optInitData['visible'] = True
            return optInitData
