# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/legacy/meta/DamagePanelMeta.py
from gui.Scaleform.daapi.view.battle.legacy.meta.BattleComponentMeta import BattleComponentMeta

class DamagePanelMeta(BattleComponentMeta):

    def clickToTankmanIcon(self, entityName):
        raise NotImplementedError

    def clickToDeviceIcon(self, entityName):
        raise NotImplementedError

    def clickToFireIcon(self):
        raise NotImplementedError

    def as_setPlayerInfoS(self, fullName, playerName, clanName, regionName, vehicleTypeName):
        self._flashObject.as_setPlayerInfo(fullName, playerName, clanName, regionName, vehicleTypeName)

    def as_setupS(self, health, indicatorType, crewLayout, yawLimits, hasTurretRotator, isAutoRotationOn):
        self._flashObject.as_setup(health, indicatorType, crewLayout, yawLimits, hasTurretRotator, isAutoRotationOn)

    def as_updateHealthS(self, health):
        self._flashObject.as_updateHealth(health)

    def as_updateSpeedS(self, speed):
        self._flashObject.as_updateSpeed(speed)

    def as_setCruiseModeS(self, mode):
        self._flashObject.as_setCruiseMode(mode)

    def as_setAutoRotationS(self, isOn):
        self._flashObject.as_setAutoRotation(isOn)

    def as_setFireInVehicleS(self, isInFire):
        self._flashObject.as_setFireInVehicle(isInFire)

    def as_updateDeviceStateS(self, deviceName, deviceState):
        self._flashObject.as_updateDeviceState(deviceName, deviceState)

    def as_updateRepairingDeviceS(self, deviceName, percents, seconds):
        self._flashObject.as_updateRepairingDevice(deviceName, percents, seconds)

    def as_setVehicleDestroyedS(self):
        self._flashObject.as_setVehicleDestroyed()

    def as_setCrewDeactivatedS(self):
        self._flashObject.as_setCrewDeactivated()

    def as_showS(self, isShow):
        self._flashObject.as_show(isShow)

    def as_destroyS(self):
        self._flashObject.as_destroy()

    def as_resetS(self):
        self._flashObject.as_reset()

    def as_setNormalizedEngineRpmS(self, rpm):
        self._flashObject.as_setNormalizedEngineRpm(rpm)

    def as_updateMaxSpeedS(self, speed):
        self._flashObject.as_setMaxSpeed(speed)

    def as_startVehicleStartAnimS(self):
        self._flashObject.as_startVehicleStartAnim()

    def as_finishVehicleStartAnimS(self):
        self._flashObject.as_finishVehicleStartAnim()

    def as_playEngineStartAnimS(self):
        self._flashObject.as_playEngineStartAnim()
