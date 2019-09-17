# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FestivalRaceSpeedometerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FestivalRaceSpeedometerMeta(BaseDAAPIComponent):

    def as_updateSpeedS(self, value):
        return self.flashObject.as_updateSpeed(value) if self._isDAAPIInited() else None

    def as_updateEquipmentStageS(self, value):
        return self.flashObject.as_updateEquipmentStage(value) if self._isDAAPIInited() else None

    def as_resetS(self):
        return self.flashObject.as_reset() if self._isDAAPIInited() else None
