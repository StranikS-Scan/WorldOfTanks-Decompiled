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

    def as_setChatCommandsVisibilityS(self, value):
        return self.flashObject.as_setChatCommandsVisibility(value) if self._isDAAPIInited() else None

    def as_setPlayerHPS(self, isAlly, index, percent):
        return self.flashObject.as_setPlayerHP(isAlly, index, percent) if self._isDAAPIInited() else None

    def as_setOverrideExInfoS(self, exOverrideInfo):
        return self.flashObject.as_setOverrideExInfo(exOverrideInfo) if self._isDAAPIInited() else None

    def as_setPanelHPBarVisibilityStateS(self, value):
        return self.flashObject.as_setPanelHPBarVisibilityState(value) if self._isDAAPIInited() else None
