# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SiegeModeIndicatorMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class SiegeModeIndicatorMeta(BaseDAAPIComponent):

    def as_switchSiegeStateS(self, totalTime, leftTime, siegeState, moduleState, isSmooth):
        return self.flashObject.as_switchSiegeState(totalTime, leftTime, siegeState, moduleState, isSmooth) if self._isDAAPIInited() else None

    def as_setAutoSiegeModeStateS(self, siegeState, moduleState):
        return self.flashObject.as_setAutoSiegeModeState(siegeState, moduleState) if self._isDAAPIInited() else None

    def as_switchSiegeStateSnapshotS(self, totalTime, leftTime, siegeState, moduleState, isSmooth):
        return self.flashObject.as_switchSiegeStateSnapshot(totalTime, leftTime, siegeState, moduleState, isSmooth) if self._isDAAPIInited() else None

    def as_updateDeviceStateS(self, deviceName, deviceState):
        return self.flashObject.as_updateDeviceState(deviceName, deviceState) if self._isDAAPIInited() else None

    def as_updateLayoutS(self, x, y):
        return self.flashObject.as_updateLayout(x, y) if self._isDAAPIInited() else None

    def as_setVisibleS(self, visible):
        return self.flashObject.as_setVisible(visible) if self._isDAAPIInited() else None

    def as_setSiegeModeTypeS(self, type):
        return self.flashObject.as_setSiegeModeType(type) if self._isDAAPIInited() else None
