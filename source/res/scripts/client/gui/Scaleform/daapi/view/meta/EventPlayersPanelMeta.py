# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventPlayersPanelMeta.py
from gui.Scaleform.daapi.view.battle.classic.players_panel import PlayersPanel

class EventPlayersPanelMeta(PlayersPanel):

    def as_setIsBossS(self, value):
        return self.flashObject.as_setIsBoss(value) if self._isDAAPIInited() else None

    def as_setBossBotInfoS(self, data):
        return self.flashObject.as_setBossBotInfo(data) if self._isDAAPIInited() else None

    def as_updateBossBotHpS(self, vehID, hpMax, hpCurrent):
        return self.flashObject.as_updateBossBotHp(vehID, hpMax, hpCurrent) if self._isDAAPIInited() else None

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

    def as_setIsDestroyedS(self, id, value):
        return self.flashObject.as_setIsDestroyed(id, value) if self._isDAAPIInited() else None

    def as_resetGeneratorCaptureTimerS(self, id):
        return self.flashObject.as_resetGeneratorCaptureTimer(id) if self._isDAAPIInited() else None

    def as_lockGeneratorS(self, id, value):
        return self.flashObject.as_lockGenerator(id, value) if self._isDAAPIInited() else None

    def as_updateGeneratorDownTimeS(self, id, totalTime, remainingTime, captureTimeText):
        return self.flashObject.as_updateGeneratorDownTime(id, totalTime, remainingTime, captureTimeText) if self._isDAAPIInited() else None
