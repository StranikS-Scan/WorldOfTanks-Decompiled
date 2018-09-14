# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AimMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class AimMeta(BaseDAAPIModule):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIModule
    null
    """

    def as_initSettingsS(self, centerAlphaValue, centerType, netAlphaValue, netType, reloaderAlphaValue, reloaderType, conditionAlphaValue, conditionType, cassetteAlphaValue, cassetteType, reloaderTimerAlphaValue, reloaderTimerType):
        """
        :param centerAlphaValue:
        :param centerType:
        :param netAlphaValue:
        :param netType:
        :param reloaderAlphaValue:
        :param reloaderType:
        :param conditionAlphaValue:
        :param conditionType:
        :param cassetteAlphaValue:
        :param cassetteType:
        :param reloaderTimerAlphaValue:
        :param reloaderTimerType:
        :return :
        """
        return self.flashObject.as_initSettings(centerAlphaValue, centerType, netAlphaValue, netType, reloaderAlphaValue, reloaderType, conditionAlphaValue, conditionType, cassetteAlphaValue, cassetteType, reloaderTimerAlphaValue, reloaderTimerType) if self._isDAAPIInited() else None

    def as_recreateDeviceS(self, offsetX, offsetY):
        """
        :param offsetX:
        :param offsetY:
        :return :
        """
        return self.flashObject.as_recreateDevice(offsetX, offsetY) if self._isDAAPIInited() else None

    def as_setupReloadingCounterS(self, visible):
        """
        :param visible:
        :return :
        """
        return self.flashObject.as_setupReloadingCounter(visible) if self._isDAAPIInited() else None

    def as_setReloadingS(self, duration, startTime, isReloading, currentPosition, baseTime):
        """
        :param duration:
        :param startTime:
        :param isReloading:
        :param currentPosition:
        :param baseTime:
        :return :
        """
        return self.flashObject.as_setReloading(duration, startTime, isReloading, currentPosition, baseTime) if self._isDAAPIInited() else None

    def as_setReloadingAsPercentS(self, percent, isReloading):
        """
        :param percent:
        :param isReloading:
        :return :
        """
        return self.flashObject.as_setReloadingAsPercent(percent, isReloading) if self._isDAAPIInited() else None

    def as_correctReloadingTimeS(self, time):
        """
        :param time:
        :return :
        """
        return self.flashObject.as_correctReloadingTime(time) if self._isDAAPIInited() else None

    def as_setReloadingTimeWithCorrectionS(self, duration, startTime, remainingTime):
        """
        :param duration:
        :param startTime:
        :param remainingTime:
        :return :
        """
        return self.flashObject.as_setReloadingTimeWithCorrection(duration, startTime, remainingTime) if self._isDAAPIInited() else None

    def as_setHealthS(self, percent):
        """
        :param percent:
        :return :
        """
        return self.flashObject.as_setHealth(percent) if self._isDAAPIInited() else None

    def as_setAmmoStockS(self, quantity, quantityInClip, isLow, clipState, clipReloaded):
        """
        :param quantity:
        :param quantityInClip:
        :param isLow:
        :param clipState:
        :param clipReloaded:
        :return :
        """
        return self.flashObject.as_setAmmoStock(quantity, quantityInClip, isLow, clipState, clipReloaded) if self._isDAAPIInited() else None

    def as_setClipParamsS(self, clipCapacity, burst):
        """
        :param clipCapacity:
        :param burst:
        :return :
        """
        return self.flashObject.as_setClipParams(clipCapacity, burst) if self._isDAAPIInited() else None

    def as_setTargetS(self, name, type, color):
        """
        :param name:
        :param type:
        :param color:
        :return :
        """
        return self.flashObject.as_setTarget(name, type, color) if self._isDAAPIInited() else None

    def as_clearTargetS(self, startTime):
        """
        :param startTime:
        :return :
        """
        return self.flashObject.as_clearTarget(startTime) if self._isDAAPIInited() else None

    def as_updateTargetS(self, dist):
        """
        :param dist:
        :return :
        """
        return self.flashObject.as_updateTarget(dist) if self._isDAAPIInited() else None

    def as_updatePlayerInfoS(self, info):
        """
        :param info:
        :return :
        """
        return self.flashObject.as_updatePlayerInfo(info) if self._isDAAPIInited() else None

    def as_updateAmmoStateS(self, hasAmmo):
        """
        :param hasAmmo:
        :return :
        """
        return self.flashObject.as_updateAmmoState(hasAmmo) if self._isDAAPIInited() else None

    def as_updateAmmoInfoPosS(self):
        """
        :return :
        """
        return self.flashObject.as_updateAmmoInfoPos() if self._isDAAPIInited() else None

    def as_updateAdjustS(self, brightness, contrast, saturation, hue):
        """
        :param brightness:
        :param contrast:
        :param saturation:
        :param hue:
        :return :
        """
        return self.flashObject.as_updateAdjust(brightness, contrast, saturation, hue) if self._isDAAPIInited() else None

    def as_updateDistanceS(self, dist):
        """
        :param dist:
        :return :
        """
        return self.flashObject.as_updateDistance(dist) if self._isDAAPIInited() else None

    def as_updateReloadingBaseTimeS(self, baseTime, isReloaded):
        """
        :param baseTime:
        :param isReloaded:
        :return :
        """
        return self.flashObject.as_updateReloadingBaseTime(baseTime, isReloaded) if self._isDAAPIInited() else None

    def as_clearPreviousCorrectionS(self):
        """
        :return :
        """
        return self.flashObject.as_clearPreviousCorrection() if self._isDAAPIInited() else None

    def as_setZoomS(self, zoomStr):
        """
        :param zoomStr:
        :return :
        """
        return self.flashObject.as_setZoom(zoomStr) if self._isDAAPIInited() else None
