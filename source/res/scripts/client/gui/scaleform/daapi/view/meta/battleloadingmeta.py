# Embedded file name: battleloadingmeta
from gui.Scaleform.framework.entities.View import View

class BattleLoadingMeta(View):

    def as_setProgressS(self, val):
        try:
            if self._isDAAPIInited():
                return self.flashObject.as_setProgress(val)
        except:
            return

    def as_setTipS(self, val):
        try:
            if self._isDAAPIInited():
                return self.flashObject.as_setTip(val)
        except:
            return

    def as_setTipTitleS(self, title):
        try:
            if self._isDAAPIInited():
                return self.flashObject.as_setTipTitle(title)
        except:
            return

    def as_setEventInfoPanelDataS(self, data):
        try:
            if self._isDAAPIInited():
                return self.flashObject.as_setEventInfoPanelData(data)
        except:
            return

    def as_setArenaInfoS(self, data):
        try:
            if self._isDAAPIInited():
                return self.flashObject.as_setArenaInfo(data)
        except:
            return

    def as_setMapIconS(self, source):
        try:
            if self._isDAAPIInited():
                return self.flashObject.as_setMapIcon(source)
        except:
            return

    def as_setPlayerDataS(self, playerVehicleID, prebattleID):
        try:
            if self._isDAAPIInited():
                return self.flashObject.as_setPlayerData(playerVehicleID, prebattleID)
        except:
            return

    def as_setVehiclesDataS(self, data):
        try:
            if self._isDAAPIInited():
                return self.flashObject.as_setVehiclesData(data)
        except:
            return

    def as_addVehicleInfoS(self, data):
        try:
            if self._isDAAPIInited():
                return self.flashObject.as_addVehicleInfo(data)
        except:
            return

    def as_updateVehicleInfoS(self, data):
        try:
            if self._isDAAPIInited():
                return self.flashObject.as_updateVehicleInfo(data)
        except:
            return

    def as_setVehicleStatusS(self, data):
        try:
            if self._isDAAPIInited():
                return self.flashObject.as_setVehicleStatus(data)
        except:
            return

    def as_setPlayerStatusS(self, data):
        try:
            if self._isDAAPIInited():
                return self.flashObject.as_setPlayerStatus(data)
        except:
            return
