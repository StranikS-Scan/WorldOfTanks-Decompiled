# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleRoyaleTeamPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleRoyaleTeamPanelMeta(BaseDAAPIComponent):

    def as_setInitDataS(self, title, names, clans, playerTeamIndex):
        return self.flashObject.as_setInitData(title, names, clans, playerTeamIndex) if self._isDAAPIInited() else None

    def as_setPlayerStateS(self, index, accountDBID, vID, teamIndex, alive, ready, hpPercent, fragsCount, vehicleLevel, icon):
        return self.flashObject.as_setPlayerState(index, accountDBID, vID, teamIndex, alive, ready, hpPercent, fragsCount, vehicleLevel, icon) if self._isDAAPIInited() else None

    def as_setPlayerStatusS(self, index, alive, ready, isRespawning=False):
        return self.flashObject.as_setPlayerStatus(index, alive, ready, isRespawning) if self._isDAAPIInited() else None

    def as_setPlayerHPS(self, index, percent):
        return self.flashObject.as_setPlayerHP(index, percent) if self._isDAAPIInited() else None

    def as_setPlayerFragsS(self, index, count):
        return self.flashObject.as_setPlayerFrags(index, count) if self._isDAAPIInited() else None

    def as_setVehicleLevelS(self, index, level):
        return self.flashObject.as_setVehicleLevel(index, level) if self._isDAAPIInited() else None

    def as_setPlayerVehicleS(self, index, icon):
        return self.flashObject.as_setPlayerVehicle(index, icon) if self._isDAAPIInited() else None
