# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/meta/PortalEnemiesPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PortalEnemiesPanelMeta(BaseDAAPIComponent):

    def as_setCurrentPhaseS(self, value):
        return self.flashObject.as_setCurrentPhase(value) if self._isDAAPIInited() else None

    def as_setPhasesCountS(self, value):
        return self.flashObject.as_setPhasesCount(value) if self._isDAAPIInited() else None

    def as_setLaneVehicleInfoS(self, laneIndex, heavyCount, mediumCount, lightCount):
        return self.flashObject.as_setLaneVehicleInfo(laneIndex, heavyCount, mediumCount, lightCount) if self._isDAAPIInited() else None

    def as_setBuffStatusVisibleS(self, value):
        return self.flashObject.as_setBuffStatusVisible(value) if self._isDAAPIInited() else None

    def as_resetStateS(self):
        return self.flashObject.as_resetState() if self._isDAAPIInited() else None
