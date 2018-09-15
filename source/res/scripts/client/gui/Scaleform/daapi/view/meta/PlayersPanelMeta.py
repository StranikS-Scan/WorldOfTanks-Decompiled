# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PlayersPanelMeta.py
from gui.Scaleform.daapi.view.battle.classic.base_stats import StatsBase

class PlayersPanelMeta(StatsBase):

    def tryToSetPanelModeByMouse(self, panelMode):
        self._printOverrideError('tryToSetPanelModeByMouse')

    def switchToOtherPlayer(self, vehicleID):
        self._printOverrideError('switchToOtherPlayer')

    def as_setPanelModeS(self, value):
        return self.flashObject.as_setPanelMode(value) if self._isDAAPIInited() else None

    def as_setEnemyHideStatusS(self, hidden):
        return self.flashObject.as_setEnemyHideStatus(hidden) if self._isDAAPIInited() else None
