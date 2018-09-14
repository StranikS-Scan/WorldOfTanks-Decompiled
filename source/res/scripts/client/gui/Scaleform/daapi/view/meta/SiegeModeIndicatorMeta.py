# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SiegeModeIndicatorMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class SiegeModeIndicatorMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def as_switchSiegeStateS(self, totalTime, leftTime, siegeState, engineState):
        return self.flashObject.as_switchSiegeState(totalTime, leftTime, siegeState, engineState) if self._isDAAPIInited() else None

    def as_switchSiegeStateSnapshotS(self, totalTime, leftTime, siegeState, engineState):
        return self.flashObject.as_switchSiegeStateSnapshot(totalTime, leftTime, siegeState, engineState) if self._isDAAPIInited() else None

    def as_updateDeviceStateS(self, deviceName, deviceState):
        return self.flashObject.as_updateDeviceState(deviceName, deviceState) if self._isDAAPIInited() else None

    def as_updateLayoutS(self, x, y):
        return self.flashObject.as_updateLayout(x, y) if self._isDAAPIInited() else None

    def as_setVisibleS(self, visible):
        return self.flashObject.as_setVisible(visible) if self._isDAAPIInited() else None

    def as_showHintS(self, buttonName, messageLeft, messageRight):
        return self.flashObject.as_showHint(buttonName, messageLeft, messageRight) if self._isDAAPIInited() else None

    def as_hideHintS(self):
        return self.flashObject.as_hideHint() if self._isDAAPIInited() else None
