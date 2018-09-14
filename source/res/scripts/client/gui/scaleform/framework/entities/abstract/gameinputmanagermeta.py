# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/GameInputManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class GameInputManagerMeta(BaseDAAPIModule):

    def handleGlobalKeyEvent(self, keyCode, eventType):
        self._printOverrideError('handleGlobalKeyEvent')

    def as_addKeyHandlerS(self, keyCode, eventType, ignoreText, cancelEventType):
        if self._isDAAPIInited():
            return self.flashObject.as_addKeyHandler(keyCode, eventType, ignoreText, cancelEventType)

    def as_clearKeyHandlerS(self, keyCode, eventType):
        if self._isDAAPIInited():
            return self.flashObject.as_clearKeyHandler(keyCode, eventType)
