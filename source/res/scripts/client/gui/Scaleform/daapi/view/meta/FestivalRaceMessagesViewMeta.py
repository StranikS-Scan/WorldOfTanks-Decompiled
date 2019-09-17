# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FestivalRaceMessagesViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FestivalRaceMessagesViewMeta(BaseDAAPIComponent):

    def as_showMessageS(self, messageType, title, value):
        return self.flashObject.as_showMessage(messageType, title, value) if self._isDAAPIInited() else None

    def as_hideMessageS(self):
        return self.flashObject.as_hideMessage() if self._isDAAPIInited() else None
