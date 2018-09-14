# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FalloutMultiTeamLoadingMeta.py
from gui.Scaleform.framework.entities.View import View

class FalloutMultiTeamLoadingMeta(View):

    def as_setProgressS(self, progressValue):
        if self._isDAAPIInited():
            return self.flashObject.as_setProgress(progressValue)

    def as_setEventInfoPanelDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setEventInfoPanelData(data)

    def as_setArenaInfoS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setArenaInfo(data)

    def as_setPlayerDataS(self, playerVehicleID, prebattleID):
        if self._isDAAPIInited():
            return self.flashObject.as_setPlayerData(playerVehicleID, prebattleID)

    def as_setVehiclesDataS(self, vehiclesInfos):
        if self._isDAAPIInited():
            return self.flashObject.as_setVehiclesData(vehiclesInfos)

    def as_addVehicleInfoS(self, vehicleInfo, vehiclesIDs):
        if self._isDAAPIInited():
            return self.flashObject.as_addVehicleInfo(vehicleInfo, vehiclesIDs)

    def as_updateVehicleInfoS(self, vehicleInfo, vehiclesIDs):
        if self._isDAAPIInited():
            return self.flashObject.as_updateVehicleInfo(vehicleInfo, vehiclesIDs)

    def as_setVehicleStatusS(self, vehicleID, status, vehiclesIDs):
        if self._isDAAPIInited():
            return self.flashObject.as_setVehicleStatus(vehicleID, status, vehiclesIDs)

    def as_setPlayerStatusS(self, vehicleID, status):
        if self._isDAAPIInited():
            return self.flashObject.as_setPlayerStatus(vehicleID, status)
