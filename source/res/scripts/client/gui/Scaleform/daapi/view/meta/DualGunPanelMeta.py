# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DualGunPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class DualGunPanelMeta(BaseDAAPIComponent):

    def as_resetS(self):
        return self.flashObject.as_reset() if self._isDAAPIInited() else None

    def as_setViewS(self, viewId):
        return self.flashObject.as_setView(viewId) if self._isDAAPIInited() else None

    def as_setVisibleS(self, visible):
        return self.flashObject.as_setVisible(visible) if self._isDAAPIInited() else None

    def as_setPlaybackSpeedS(self, value):
        return self.flashObject.as_setPlaybackSpeed(value) if self._isDAAPIInited() else None

    def as_updateActiveGunS(self, activeGunId, timeLeft, totalTime):
        return self.flashObject.as_updateActiveGun(activeGunId, timeLeft, totalTime) if self._isDAAPIInited() else None

    def as_readyForChargeS(self):
        return self.flashObject.as_readyForCharge() if self._isDAAPIInited() else None

    def as_setGunStateS(self, gunId, state, timeLeft, totalTime):
        return self.flashObject.as_setGunState(gunId, state, timeLeft, totalTime) if self._isDAAPIInited() else None

    def as_startChargingS(self, timeLeft, totalTime):
        return self.flashObject.as_startCharging(timeLeft, totalTime) if self._isDAAPIInited() else None

    def as_cancelChargeS(self):
        return self.flashObject.as_cancelCharge() if self._isDAAPIInited() else None

    def as_setCooldownS(self, timeLeft):
        return self.flashObject.as_setCooldown(timeLeft) if self._isDAAPIInited() else None

    def as_setDualShotModeS(self):
        return self.flashObject.as_setDualShotMode() if self._isDAAPIInited() else None

    def as_collapsePanelS(self):
        return self.flashObject.as_collapsePanel() if self._isDAAPIInited() else None

    def as_expandPanelS(self):
        return self.flashObject.as_expandPanel() if self._isDAAPIInited() else None

    def as_setReloadingTimeIncreasedS(self, hasNegativeEffect):
        return self.flashObject.as_setReloadingTimeIncreased(hasNegativeEffect) if self._isDAAPIInited() else None

    def as_updateTotalTimeS(self, value):
        return self.flashObject.as_updateTotalTime(value) if self._isDAAPIInited() else None

    def as_setTimerVisibleS(self, value):
        return self.flashObject.as_setTimerVisible(value) if self._isDAAPIInited() else None
