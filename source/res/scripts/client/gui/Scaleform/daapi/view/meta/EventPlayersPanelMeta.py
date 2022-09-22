# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventPlayersPanelMeta.py
from gui.Scaleform.daapi.view.battle.classic.players_panel import PlayersPanel

class EventPlayersPanelMeta(PlayersPanel):

    def as_setIsBossS(self, value):
        return self.flashObject.as_setIsBoss(value) if self._isDAAPIInited() else None

    def as_setBossBotInfoS(self, data):
        return self.flashObject.as_setBossBotInfo(data) if self._isDAAPIInited() else None

    def as_updateBossBombTimerS(self, id, timeLeft, timeTotal, replaySpeed=1):
        return self.flashObject.as_updateBossBombTimer(id, timeLeft, timeTotal, replaySpeed) if self._isDAAPIInited() else None

    def as_updateBossBotHpS(self, vehID, hpMax, hpCurrent):
        return self.flashObject.as_updateBossBotHp(vehID, hpMax, hpCurrent) if self._isDAAPIInited() else None

    def as_setBossBotSpottedS(self, vehID, status):
        return self.flashObject.as_setBossBotSpotted(vehID, status) if self._isDAAPIInited() else None

    def as_clearBossBotCampS(self, campId):
        return self.flashObject.as_clearBossBotCamp(campId) if self._isDAAPIInited() else None
