# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BRRespawnMessagePanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BRRespawnMessagePanelMeta(BaseDAAPIComponent):

    def as_addMessageS(self, data):
        return self.flashObject.as_addMessage(data) if self._isDAAPIInited() else None

    def as_hideMessageS(self):
        return self.flashObject.as_hideMessage() if self._isDAAPIInited() else None

    def as_setMessageTimeS(self, seconds):
        return self.flashObject.as_setMessageTime(seconds) if self._isDAAPIInited() else None
