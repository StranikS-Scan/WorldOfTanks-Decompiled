# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MinionDeathPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class MinionDeathPanelMeta(BaseDAAPIComponent):

    def onBattleLoadCompleted(self):
        self._printOverrideError('onBattleLoadCompleted')

    def as_showPanelS(self):
        return self.flashObject.as_showPanel() if self._isDAAPIInited() else None

    def as_hidePanelS(self):
        return self.flashObject.as_hidePanel() if self._isDAAPIInited() else None

    def as_updateDeadCountS(self, newValue, total):
        return self.flashObject.as_updateDeadCount(newValue, total) if self._isDAAPIInited() else None

    def as_initPanelS(self, data):
        """
        :param data: Represented by MinionDeathVO (AS)
        """
        return self.flashObject.as_initPanel(data) if self._isDAAPIInited() else None
