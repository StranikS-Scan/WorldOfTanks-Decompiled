# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventBossWidgetMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventBossWidgetMeta(BaseDAAPIComponent):

    def as_setWidgetDataS(self, data):
        return self.flashObject.as_setWidgetData(data) if self._isDAAPIInited() else None

    def as_updateHpS(self, hpCurrent):
        return self.flashObject.as_updateHp(hpCurrent) if self._isDAAPIInited() else None

    def as_updateKillsS(self, kills):
        return self.flashObject.as_updateKills(kills) if self._isDAAPIInited() else None

    def as_updateGeneratorsS(self, availableCount):
        return self.flashObject.as_updateGenerators(availableCount) if self._isDAAPIInited() else None

    def as_updateDebuffS(self, totalTime, remainingTime):
        return self.flashObject.as_updateDebuff(totalTime, remainingTime) if self._isDAAPIInited() else None

    def as_updateHyperionChargeS(self, count, maxCount):
        return self.flashObject.as_updateHyperionCharge(count, maxCount) if self._isDAAPIInited() else None

    def as_updateGeneratorsChargingS(self, id, progress):
        return self.flashObject.as_updateGeneratorsCharging(id, progress) if self._isDAAPIInited() else None

    def as_resetGeneratorCaptureTimerS(self, id):
        return self.flashObject.as_resetGeneratorCaptureTimer(id) if self._isDAAPIInited() else None
