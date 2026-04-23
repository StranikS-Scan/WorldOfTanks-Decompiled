# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/meta/BattleHintProgressDefenceMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleHintProgressDefenceMeta(BaseDAAPIComponent):

    def as_updateProgressS(self, value, progressValue, pointsLeft):
        return self.flashObject.as_updateProgress(value, progressValue, pointsLeft) if self._isDAAPIInited() else None

    def as_updateHealthPointsS(self, nextWavePoints):
        return self.flashObject.as_updateHealthPoints(nextWavePoints) if self._isDAAPIInited() else None

    def as_updateVehiclesS(self, vehicles):
        return self.flashObject.as_updateVehicles(vehicles) if self._isDAAPIInited() else None

    def as_handleAsReplayS(self):
        return self.flashObject.as_handleAsReplay() if self._isDAAPIInited() else None
