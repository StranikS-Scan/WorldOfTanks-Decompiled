# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AimMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class AimMeta(BaseDAAPIModule):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIModule
    """

    def as_initSettingsS(self, centerAlphaValue, centerType, netAlphaValue, netType, reloaderAlphaValue, reloaderType, conditionAlphaValue, conditionType, cassetteAlphaValue, cassetteType, reloaderTimerAlphaValue, reloaderTimerType):
        return self.flashObject.as_initSettings(centerAlphaValue, centerType, netAlphaValue, netType, reloaderAlphaValue, reloaderType, conditionAlphaValue, conditionType, cassetteAlphaValue, cassetteType, reloaderTimerAlphaValue, reloaderTimerType) if self._isDAAPIInited() else None

    def as_recreateDeviceS(self, offsetX, offsetY):
        return self.flashObject.as_recreateDevice(offsetX, offsetY) if self._isDAAPIInited() else None

    def as_setupReloadingCounterS(self, visible):
        return self.flashObject.as_setupReloadingCounter(visible) if self._isDAAPIInited() else None

    def as_setReloadingS(self, duration, startTime, isReloading, currentPosition, baseTime):
        return self.flashObject.as_setReloading(duration, startTime, isReloading, currentPosition, baseTime) if self._isDAAPIInited() else None

    def as_setReloadingAsPercentS(self, percent, isReloading):
        return self.flashObject.as_setReloadingAsPercent(percent, isReloading) if self._isDAAPIInited() else None

    def as_correctReloadingTimeS(self, time):
        return self.flashObject.as_correctReloadingTime(time) if self._isDAAPIInited() else None

    def as_setReloadingTimeWithCorrectionS(self, duration, startTime, remainingTime):
        return self.flashObject.as_setReloadingTimeWithCorrection(duration, startTime, remainingTime) if self._isDAAPIInited() else None

    def as_setHealthS(self, percent):
        return self.flashObject.as_setHealth(percent) if self._isDAAPIInited() else None

    def as_setAmmoStockS(self, quantity, quantityInClip, isLow, clipState, clipReloaded):
        return self.flashObject.as_setAmmoStock(quantity, quantityInClip, isLow, clipState, clipReloaded) if self._isDAAPIInited() else None

    def as_setClipParamsS(self, clipCapacity, burst):
        return self.flashObject.as_setClipParams(clipCapacity, burst) if self._isDAAPIInited() else None

    def as_setTargetS(self, name, type, color):
        return self.flashObject.as_setTarget(name, type, color) if self._isDAAPIInited() else None

    def as_clearTargetS(self, startTime):
        return self.flashObject.as_clearTarget(startTime) if self._isDAAPIInited() else None

    def as_updateTargetS(self, dist):
        return self.flashObject.as_updateTarget(dist) if self._isDAAPIInited() else None

    def as_updatePlayerInfoS(self, info):
        return self.flashObject.as_updatePlayerInfo(info) if self._isDAAPIInited() else None

    def as_updateAmmoStateS(self, hasAmmo):
        return self.flashObject.as_updateAmmoState(hasAmmo) if self._isDAAPIInited() else None

    def as_updateAmmoInfoPosS(self):
        return self.flashObject.as_updateAmmoInfoPos() if self._isDAAPIInited() else None

    def as_updateAdjustS(self, brightness, contrast, saturation, hue):
        return self.flashObject.as_updateAdjust(brightness, contrast, saturation, hue) if self._isDAAPIInited() else None

    def as_updateDistanceS(self, dist):
        return self.flashObject.as_updateDistance(dist) if self._isDAAPIInited() else None

    def as_updateReloadingBaseTimeS(self, baseTime, isReloaded):
        return self.flashObject.as_updateReloadingBaseTime(baseTime, isReloaded) if self._isDAAPIInited() else None

    def as_clearPreviousCorrectionS(self):
        return self.flashObject.as_clearPreviousCorrection() if self._isDAAPIInited() else None

    def as_setZoomS(self, zoomStr):
        return self.flashObject.as_setZoom(zoomStr) if self._isDAAPIInited() else None
