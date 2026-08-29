# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/meta/WhiteTigerPlayersPanelMeta.py
from gui.Scaleform.daapi.view.battle.classic.players_panel import PlayersPanel

class WhiteTigerPlayersPanelMeta(PlayersPanel):

    def as_setIsBossS(self, value):
        return self.flashObject.as_setIsBoss(value) if self._isDAAPIInited() else None

    def as_setBossBotInfoS(self, data):
        return self.flashObject.as_setBossBotInfo(data) if self._isDAAPIInited() else None

    def as_updateBossBotHpS(self, vehID, hpMax, hpCurrent):
        return self.flashObject.as_updateBossBotHp(vehID, hpMax, hpCurrent) if self._isDAAPIInited() else None

    def as_setPlasmaForVehiclesS(self, vehID, plasmaValue):
        return self.flashObject.as_setPlasmaForVehicles(vehID, plasmaValue) if self._isDAAPIInited() else None

    def as_setBossBotSpottedS(self, vehID, status):
        return self.flashObject.as_setBossBotSpotted(vehID, status) if self._isDAAPIInited() else None

    def as_clearBossBotCampS(self, campId):
        return self.flashObject.as_clearBossBotCamp(campId) if self._isDAAPIInited() else None

    def as_setAllBossBotCampsOfflineS(self):
        return self.flashObject.as_setAllBossBotCampsOffline() if self._isDAAPIInited() else None

    def as_updateCampInfoStatusS(self, campId):
        return self.flashObject.as_updateCampInfoStatus(campId) if self._isDAAPIInited() else None

    def as_updateGeneratorCaptureTimerS(self, id, timeLeft, progress, numInvaders, speed):
        return self.flashObject.as_updateGeneratorCaptureTimer(id, timeLeft, progress, numInvaders, speed) if self._isDAAPIInited() else None

    def as_setIsDestroyedS(self, id):
        return self.flashObject.as_setIsDestroyed(id) if self._isDAAPIInited() else None

    def as_resetGeneratorCaptureTimerS(self, id):
        return self.flashObject.as_resetGeneratorCaptureTimer(id) if self._isDAAPIInited() else None

    def as_lockGeneratorS(self, id, value):
        return self.flashObject.as_lockGenerator(id, value) if self._isDAAPIInited() else None

    def as_updateGeneratorDownTimeS(self, id, captureTimeText):
        return self.flashObject.as_updateGeneratorDownTime(id, captureTimeText) if self._isDAAPIInited() else None

    def as_setColorBlindS(self, isColorBlind):
        return self.flashObject.as_setColorBlind(isColorBlind) if self._isDAAPIInited() else None
