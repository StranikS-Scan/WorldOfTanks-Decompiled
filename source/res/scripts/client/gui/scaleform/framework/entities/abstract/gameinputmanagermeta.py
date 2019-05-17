# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/GameInputManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class GameInputManagerMeta(BaseDAAPIComponent):

    def handleGlobalKeyEvent(self, keyCode, eventType):
        self._printOverrideError('handleGlobalKeyEvent')

    def as_addKeyHandlerS(self, keyCode, eventType, ignoreText, cancelEventType=None, handlerPriority=0):
        return self.flashObject.as_addKeyHandler(keyCode, eventType, ignoreText, cancelEventType, handlerPriority) if self._isDAAPIInited() else None

    def as_clearKeyHandlerS(self, keyCode, eventType):
        return self.flashObject.as_clearKeyHandler(keyCode, eventType) if self._isDAAPIInited() else None
