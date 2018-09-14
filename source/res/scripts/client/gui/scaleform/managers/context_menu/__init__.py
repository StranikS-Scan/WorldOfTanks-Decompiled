# Embedded file name: scripts/client/gui/Scaleform/managers/context_menu/__init__.py
from debug_utils import LOG_WARNING
from gui.Scaleform.framework.entities.abstract.ContextMenuManagerMeta import ContextMenuManagerMeta
from gui.shared.utils import class_for_name

class ContextMenuManager(ContextMenuManagerMeta):
    _handlersMap = {}

    def __init__(self, app):
        super(ContextMenuManager, self).__init__()
        self.seEnvironment(app)
        self.__currentHandler = None
        self._handlersMap = self._initializeHandlers(self._handlersMap)
        return

    def _initializeHandlers(self, handlers):
        initedHandlers = {}
        for handlerType, (handlerModule, handlerClass) in handlers.iteritems():
            initedHandlers[handlerType] = class_for_name(handlerModule, handlerClass)

        return initedHandlers

    def getCurrentHandler(self):
        return self.__currentHandler

    def pyHide(self):
        self.as_hideS()

    @classmethod
    def registerHandler(cls, handlerType, handlerModule, handlerClass):
        if handlerType not in cls._handlersMap:
            cls._handlersMap[handlerType] = (handlerModule, handlerClass)

    def requestOptions(self, handlerType, ctx):
        self.__currentHandler = self._getHandler(handlerType, ctx)
        if self.__currentHandler is not None:
            self.__currentHandler.onContextMenuHide += self.as_hideS
            self._sendOptionsToFlash(self.__currentHandler.getOptions(ctx))
        return

    def onOptionSelect(self, optionId):
        if self.__currentHandler is not None:
            self.__currentHandler.onOptionSelect(optionId)
        return

    def onHide(self):
        self.__disposeHandler()

    def _dispose(self):
        self.__app = None
        self._handlersMap.clear()
        self._handlersMap = None
        self.__disposeHandler()
        super(ContextMenuManager, self)._dispose()
        return

    def _getHandler(self, handlerType, ctx):
        if handlerType in self._handlersMap:
            return self._handlersMap[handlerType](self, ctx)
        else:
            LOG_WARNING('Unknown context menu handler type', handlerType, ctx)
            return None

    def _sendOptionsToFlash(self, options):
        self.as_setOptionsS({'options': options})

    def _onOptionsChanged(self, options):
        self._sendOptionsToFlash(options)

    def __disposeHandler(self):
        if self.__currentHandler is not None:
            self.__currentHandler.onContextMenuHide -= self.as_hideS
            self.__currentHandler.fini()
            self.__currentHandler = None
        return
