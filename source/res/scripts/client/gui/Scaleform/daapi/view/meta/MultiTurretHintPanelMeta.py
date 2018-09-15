# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MultiTurretHintPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class MultiTurretHintPanelMeta(BaseDAAPIComponent):

    def onBattleLoadCompleted(self):
        self._printOverrideError('onBattleLoadCompleted')

    def as_showPanelS(self):
        return self.flashObject.as_showPanel() if self._isDAAPIInited() else None

    def as_hidePanelS(self):
        return self.flashObject.as_hidePanel() if self._isDAAPIInited() else None

    def as_submitMessagesS(self, data):
        """
        :param data: Represented by MultiTurretHintVO (AS)
        """
        return self.flashObject.as_submitMessages(data) if self._isDAAPIInited() else None
