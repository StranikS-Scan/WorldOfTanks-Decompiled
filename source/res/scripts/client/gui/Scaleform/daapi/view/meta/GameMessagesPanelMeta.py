# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/GameMessagesPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class GameMessagesPanelMeta(BaseDAAPIComponent):

    def onMessageStarted(self, type, id):
        self._printOverrideError('onMessageStarted')

    def onMessageEnded(self, type, id):
        self._printOverrideError('onMessageEnded')

    def onMessageHiding(self, type, id):
        self._printOverrideError('onMessageHiding')

    def as_addMessageS(self, messageVO):
        return self.flashObject.as_addMessage(messageVO) if self._isDAAPIInited() else None
