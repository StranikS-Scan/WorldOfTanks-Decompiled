# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DamagePanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class DamagePanelMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def clickToTankmanIcon(self, entityName):
        """
        :param entityName:
        :return :
        """
        self._printOverrideError('clickToTankmanIcon')

    def clickToDeviceIcon(self, entityName):
        """
        :param entityName:
        :return :
        """
        self._printOverrideError('clickToDeviceIcon')

    def clickToFireIcon(self):
        """
        :return :
        """
        self._printOverrideError('clickToFireIcon')

    def getTooltipData(self, entityName, state):
        """
        :param entityName:
        :param state:
        :return String:
        """
        self._printOverrideError('getTooltipData')

    def as_setPlayerInfoS(self, playerName, clanName, regionName, vehicleTypeName):
        """
        :param playerName:
        :param clanName:
        :param regionName:
        :param vehicleTypeName:
        :return :
        """
        return self.flashObject.as_setPlayerInfo(playerName, clanName, regionName, vehicleTypeName) if self._isDAAPIInited() else None

    def as_setupS(self, healthStr, progress, indicatorType, crewLayout, yawLimits, hasTurretRotator, isAutoRotationOn):
        """
        :param healthStr:
        :param progress:
        :param indicatorType:
        :param crewLayout:
        :param yawLimits:
        :param hasTurretRotator:
        :param isAutoRotationOn:
        :return :
        """
        return self.flashObject.as_setup(healthStr, progress, indicatorType, crewLayout, yawLimits, hasTurretRotator, isAutoRotationOn) if self._isDAAPIInited() else None

    def as_updateHealthS(self, healthStr, progress):
        """
        :param healthStr:
        :param progress:
        :return :
        """
        return self.flashObject.as_updateHealth(healthStr, progress) if self._isDAAPIInited() else None

    def as_updateSpeedS(self, speed):
        """
        :param speed:
        :return :
        """
        return self.flashObject.as_updateSpeed(speed) if self._isDAAPIInited() else None

    def as_setMaxSpeedS(self, maxSpeed):
        """
        :param maxSpeed:
        :return :
        """
        return self.flashObject.as_setMaxSpeed(maxSpeed) if self._isDAAPIInited() else None

    def as_setRpmVibrationS(self, intensity):
        """
        :param intensity:
        :return :
        """
        return self.flashObject.as_setRpmVibration(intensity) if self._isDAAPIInited() else None

    def as_playEngineStartAnimS(self):
        """
        :return :
        """
        return self.flashObject.as_playEngineStartAnim() if self._isDAAPIInited() else None

    def as_startVehicleStartAnimS(self):
        """
        :return :
        """
        return self.flashObject.as_startVehicleStartAnim() if self._isDAAPIInited() else None

    def as_finishVehicleStartAnimS(self):
        """
        :return :
        """
        return self.flashObject.as_finishVehicleStartAnim() if self._isDAAPIInited() else None

    def as_setNormalizedEngineRpmS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setNormalizedEngineRpm(value) if self._isDAAPIInited() else None

    def as_setCruiseModeS(self, mode):
        """
        :param mode:
        :return :
        """
        return self.flashObject.as_setCruiseMode(mode) if self._isDAAPIInited() else None

    def as_setAutoRotationS(self, isOn):
        """
        :param isOn:
        :return :
        """
        return self.flashObject.as_setAutoRotation(isOn) if self._isDAAPIInited() else None

    def as_updateDeviceStateS(self, deviceName, deviceState):
        """
        :param deviceName:
        :param deviceState:
        :return :
        """
        return self.flashObject.as_updateDeviceState(deviceName, deviceState) if self._isDAAPIInited() else None

    def as_updateRepairingDeviceS(self, deviceName, percents, seconds):
        """
        :param deviceName:
        :param percents:
        :param seconds:
        :return :
        """
        return self.flashObject.as_updateRepairingDevice(deviceName, percents, seconds) if self._isDAAPIInited() else None

    def as_setVehicleDestroyedS(self):
        """
        :return :
        """
        return self.flashObject.as_setVehicleDestroyed() if self._isDAAPIInited() else None

    def as_setCrewDeactivatedS(self):
        """
        :return :
        """
        return self.flashObject.as_setCrewDeactivated() if self._isDAAPIInited() else None

    def as_showS(self, isShow):
        """
        :param isShow:
        :return :
        """
        return self.flashObject.as_show(isShow) if self._isDAAPIInited() else None

    def as_setFireInVehicleS(self, isInFire):
        """
        :param isInFire:
        :return :
        """
        return self.flashObject.as_setFireInVehicle(isInFire) if self._isDAAPIInited() else None

    def as_setStaticDataS(self, fireMsg):
        """
        :param fireMsg:
        :return :
        """
        return self.flashObject.as_setStaticData(fireMsg) if self._isDAAPIInited() else None

    def as_resetS(self):
        """
        :return :
        """
        return self.flashObject.as_reset() if self._isDAAPIInited() else None

    def as_setPlaybackSpeedS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setPlaybackSpeed(value) if self._isDAAPIInited() else None
