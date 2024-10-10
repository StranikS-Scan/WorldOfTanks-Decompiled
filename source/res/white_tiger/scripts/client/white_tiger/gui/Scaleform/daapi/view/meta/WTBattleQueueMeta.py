# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/meta/WTBattleQueueMeta.py
from gui.Scaleform.daapi.view.lobby.battle_queue import BattleQueue

class WTBattleQueueMeta(BattleQueue):

    def onQuickStartPanelAction(self, vehID):
        self._printOverrideError('onQuickStartPanelAction')

    def as_setAverageTimeS(self, textLabel, timeLabel):
        return self.flashObject.as_setAverageTime(textLabel, timeLabel) if self._isDAAPIInited() else None

    def as_setInfoTextS(self, text):
        return self.flashObject.as_setInfoText(text) if self._isDAAPIInited() else None

    def as_showQuickStartPanelS(self, data):
        return self.flashObject.as_showQuickStartPanel(data) if self._isDAAPIInited() else None

    def as_hideQuickStartPanelS(self):
        return self.flashObject.as_hideQuickStartPanel() if self._isDAAPIInited() else None
