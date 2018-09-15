# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/abstract_switch_handler.py
from skeletons.new_year import ISwitchHandler

class AbstractSwitchHandler(ISwitchHandler):

    def __init__(self):
        self.__nextHandler = None
        self._state = None
        return

    def fini(self):
        if self.nextHandler:
            self.nextHandler.fini()

    def setNextHandler(self, handler):
        self.__nextHandler = handler

    @property
    def nextHandler(self):
        return self.__nextHandler

    def switchTo(self, state, callback=None):
        if self.nextHandler is not None:
            self.nextHandler.switchTo(state, callback)
        return

    def getSwitchHandler(self, switchHandlerType):
        handler = self
        while handler is not None:
            if isinstance(handler, switchHandlerType):
                return handler
            handler = handler.nextHandler

        return

    def _resetState(self):
        self._state = None
        if self.nextHandler:
            self.nextHandler._resetState()
        return
