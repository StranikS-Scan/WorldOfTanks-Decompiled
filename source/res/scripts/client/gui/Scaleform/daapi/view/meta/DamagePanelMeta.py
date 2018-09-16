# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DamagePanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class DamagePanelMeta(BaseDAAPIComponent):

    def clickToTankmanIcon(self, entityName):
        self._printOverrideError('clickToTankmanIcon')

    def clickToDeviceIcon(self, entityName):
        self._printOverrideError('clickToDeviceIcon')

    def clickToFireIcon(self):
        self._printOverrideError('clickToFireIcon')

    def clickToStunTimer(self):
        self._printOverrideError('clickToStunTimer')

    def getTooltipData(self, entityName, state):
        self._printOverrideError('getTooltipData')

    def as_setPlayerInfoS(self, playerName, clanName, regionName, vehicleTypeName):
        return self.flashObject.as_setPlayerInfo(playerName, clanName, regionName, vehicleTypeName) if self._isDAAPIInited() else None

    def as_setupS(self, healthStr, progress, indicatorType, crewLayout, yawLimits, hasTurretRotator, isAutoRotationOn):
        return self.flashObject.as_setup(healthStr, progress, indicatorType, crewLayout, yawLimits, hasTurretRotator, isAutoRotationOn) if self._isDAAPIInited() else None

    def as_updateHealthS(self, healthStr, progress):
        return self.flashObject.as_updateHealth(healthStr, progress) if self._isDAAPIInited() else None

    def as_updateSpeedS(self, speed):
        return self.flashObject.as_updateSpeed(speed) if self._isDAAPIInited() else None

    def as_setCruiseModeS(self, mode):
        return self.flashObject.as_setCruiseMode(mode) if self._isDAAPIInited() else None

    def as_setAutoRotationS(self, isOn):
        return self.flashObject.as_setAutoRotation(isOn) if self._isDAAPIInited() else None

    def as_updateDeviceStateS(self, deviceName, deviceState):
        return self.flashObject.as_updateDeviceState(deviceName, deviceState) if self._isDAAPIInited() else None

    def as_updateRepairingDeviceS(self, deviceName, percents, seconds):
        return self.flashObject.as_updateRepairingDevice(deviceName, percents, seconds) if self._isDAAPIInited() else None

    def as_setVehicleDestroyedS(self):
        return self.flashObject.as_setVehicleDestroyed() if self._isDAAPIInited() else None

    def as_setCrewDeactivatedS(self):
        return self.flashObject.as_setCrewDeactivated() if self._isDAAPIInited() else None

    def as_showS(self, isShow):
        return self.flashObject.as_show(isShow) if self._isDAAPIInited() else None

    def as_setFireInVehicleS(self, isInFire):
        return self.flashObject.as_setFireInVehicle(isInFire) if self._isDAAPIInited() else None

    def as_setStaticDataS(self, fireMsg):
        return self.flashObject.as_setStaticData(fireMsg) if self._isDAAPIInited() else None

    def as_resetS(self):
        return self.flashObject.as_reset() if self._isDAAPIInited() else None

    def as_setPlaybackSpeedS(self, value):
        return self.flashObject.as_setPlaybackSpeed(value) if self._isDAAPIInited() else None

    def as_showStunS(self, time, animated):
        return self.flashObject.as_showStun(time, animated) if self._isDAAPIInited() else None

    def as_hideStunS(self, animated):
        return self.flashObject.as_hideStun(animated) if self._isDAAPIInited() else None

    def as_setStunTimerSnapshotS(self, timeLeft):
        return self.flashObject.as_setStunTimerSnapshot(timeLeft) if self._isDAAPIInited() else None
