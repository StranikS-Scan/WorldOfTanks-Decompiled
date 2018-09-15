# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PvEGoalPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PvEGoalPanelMeta(BaseDAAPIComponent):

    def onBattleLoadCompleted(self):
        self._printOverrideError('onBattleLoadCompleted')

    def as_showPanelS(self):
        return self.flashObject.as_showPanel() if self._isDAAPIInited() else None

    def as_hidePanelS(self):
        return self.flashObject.as_hidePanel() if self._isDAAPIInited() else None

    def as_setMessageS(self, title, msg):
        return self.flashObject.as_setMessage(title, msg) if self._isDAAPIInited() else None
