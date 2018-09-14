# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/GameInputManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class GameInputManagerMeta(BaseDAAPIModule):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIModule
    """

    def handleGlobalKeyEvent(self, keyCode, eventType):
        self._printOverrideError('handleGlobalKeyEvent')

    def as_addKeyHandlerS(self, keyCode, eventType, ignoreText, cancelEventType):
        return self.flashObject.as_addKeyHandler(keyCode, eventType, ignoreText, cancelEventType) if self._isDAAPIInited() else None

    def as_clearKeyHandlerS(self, keyCode, eventType):
        return self.flashObject.as_clearKeyHandler(keyCode, eventType) if self._isDAAPIInited() else None
