# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleLoadingMeta.py
from gui.Scaleform.framework.entities.View import View

class BattleLoadingMeta(View):

    def as_setProgressS(self, val):
        if self._isDAAPIInited():
            return self.flashObject.as_setProgress(val)

    def as_setTipS(self, val):
        if self._isDAAPIInited():
            return self.flashObject.as_setTip(val)

    def as_setTipTitleS(self, title):
        if self._isDAAPIInited():
            return self.flashObject.as_setTipTitle(title)

    def as_setEventInfoPanelDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setEventInfoPanelData(data)

    def as_setArenaInfoS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setArenaInfo(data)

    def as_setMapIconS(self, source):
        if self._isDAAPIInited():
            return self.flashObject.as_setMapIcon(source)

    def as_setPlayerDataS(self, playerVehicleID, prebattleID):
        if self._isDAAPIInited():
            return self.flashObject.as_setPlayerData(playerVehicleID, prebattleID)

    def as_setVehiclesDataS(self, isEnemy, vehiclesInfo):
        if self._isDAAPIInited():
            return self.flashObject.as_setVehiclesData(isEnemy, vehiclesInfo)

    def as_addVehicleInfoS(self, isEnemy, vehicleInfo, vehiclesIDs):
        if self._isDAAPIInited():
            return self.flashObject.as_addVehicleInfo(isEnemy, vehicleInfo, vehiclesIDs)

    def as_updateVehicleInfoS(self, isEnemy, vehicleInfo, vehiclesIDs):
        if self._isDAAPIInited():
            return self.flashObject.as_updateVehicleInfo(isEnemy, vehicleInfo, vehiclesIDs)

    def as_setVehicleStatusS(self, isEnemy, vehicleID, status, vehiclesIDs):
        if self._isDAAPIInited():
            return self.flashObject.as_setVehicleStatus(isEnemy, vehicleID, status, vehiclesIDs)

    def as_setPlayerStatusS(self, isEnemy, vehicleID, status):
        if self._isDAAPIInited():
            return self.flashObject.as_setPlayerStatus(isEnemy, vehicleID, status)
