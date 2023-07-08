# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CrosshairPanelContainerMeta.py
from gui.Scaleform.daapi.view.meta.DAAPISimpleContainerMeta import DAAPISimpleContainerMeta

class CrosshairPanelContainerMeta(DAAPISimpleContainerMeta):

    def as_playSound(self, value):
        self._printOverrideError('as_playSound')

    def as_setSettingsS(self, data):
        return self.flashObject.as_setSettings(data) if self._isDAAPIInited() else None

    def as_setScaleS(self, scale):
        return self.flashObject.as_setScale(scale) if self._isDAAPIInited() else None

    def as_setViewS(self, viewId, settingId):
        return self.flashObject.as_setView(viewId, settingId) if self._isDAAPIInited() else None

    def as_recreateDeviceS(self, offsetX, offsetY):
        return self.flashObject.as_recreateDevice(offsetX, offsetY) if self._isDAAPIInited() else None

    def as_setReloadingCounterShownS(self, visible):
        return self.flashObject.as_setReloadingCounterShown(visible) if self._isDAAPIInited() else None

    def as_setReloadingS(self, duration, baseTime, startTime, isReloading):
        return self.flashObject.as_setReloading(duration, baseTime, startTime, isReloading) if self._isDAAPIInited() else None

    def as_setReloadingAsPercentS(self, percent, isReloading):
        return self.flashObject.as_setReloadingAsPercent(percent, isReloading) if self._isDAAPIInited() else None

    def as_setBoostAsPercentS(self, percent, duration):
        return self.flashObject.as_setBoostAsPercent(percent, duration) if self._isDAAPIInited() else None

    def as_setHealthS(self, percent):
        return self.flashObject.as_setHealth(percent) if self._isDAAPIInited() else None

    def as_setAmmoStockS(self, quantity, quantityInClip, clipState, clipReloaded=False):
        return self.flashObject.as_setAmmoStock(quantity, quantityInClip, clipState, clipReloaded) if self._isDAAPIInited() else None

    def as_setClipParamsS(self, clipCapacity, burst, isAutoloader=False):
        return self.flashObject.as_setClipParams(clipCapacity, burst, isAutoloader) if self._isDAAPIInited() else None

    def as_setDistanceS(self, dist):
        return self.flashObject.as_setDistance(dist) if self._isDAAPIInited() else None

    def as_clearDistanceS(self, immediate):
        return self.flashObject.as_clearDistance(immediate) if self._isDAAPIInited() else None

    def as_updatePlayerInfoS(self, info):
        return self.flashObject.as_updatePlayerInfo(info) if self._isDAAPIInited() else None

    def as_updateAmmoStateS(self, ammoState):
        return self.flashObject.as_updateAmmoState(ammoState) if self._isDAAPIInited() else None

    def as_setZoomS(self, zoomStr):
        return self.flashObject.as_setZoom(zoomStr) if self._isDAAPIInited() else None

    def as_createGunMarkerS(self, viewID, linkage, name):
        return self.flashObject.as_createGunMarker(viewID, linkage, name) if self._isDAAPIInited() else None

    def as_destroyGunMarkerS(self, name):
        return self.flashObject.as_destroyGunMarker(name) if self._isDAAPIInited() else None

    def as_setGunMarkerColorS(self, name, colorName):
        return self.flashObject.as_setGunMarkerColor(name, colorName) if self._isDAAPIInited() else None

    def as_setNetVisibleS(self, mask):
        return self.flashObject.as_setNetVisible(mask) if self._isDAAPIInited() else None

    def as_setNetSeparatorVisibleS(self, isVisible):
        return self.flashObject.as_setNetSeparatorVisible(isVisible) if self._isDAAPIInited() else None

    def as_setNetTypeS(self, netType):
        return self.flashObject.as_setNetType(netType) if self._isDAAPIInited() else None

    def as_autoloaderUpdateS(self, timeLeft, baseTime, isPause=False, isStun=False, isTimerOn=False, isRedText=False):
        return self.flashObject.as_autoloaderUpdate(timeLeft, baseTime, isPause, isStun, isTimerOn, isRedText) if self._isDAAPIInited() else None

    def as_setAutoloaderReloadingS(self, duration, baseTime):
        return self.flashObject.as_setAutoloaderReloading(duration, baseTime) if self._isDAAPIInited() else None

    def as_showBoostS(self, duration, baseTime):
        return self.flashObject.as_showBoost(duration, baseTime) if self._isDAAPIInited() else None

    def as_hideBoostS(self, showAnimation):
        return self.flashObject.as_hideBoost(showAnimation) if self._isDAAPIInited() else None

    def as_showShotS(self):
        return self.flashObject.as_showShot() if self._isDAAPIInited() else None

    def as_setAutoloaderReloadasPercentS(self, percent):
        return self.flashObject.as_setAutoloaderReloadasPercent(percent) if self._isDAAPIInited() else None

    def as_setAutoloaderPercentS(self, percent, sec, isTimerOn, isTimerRed):
        return self.flashObject.as_setAutoloaderPercent(percent, sec, isTimerOn, isTimerRed) if self._isDAAPIInited() else None

    def as_setSpeedModeS(self, value):
        return self.flashObject.as_setSpeedMode(value) if self._isDAAPIInited() else None

    def as_updateSpeedS(self, value):
        return self.flashObject.as_updateSpeed(value) if self._isDAAPIInited() else None

    def as_updateBurnoutS(self, value):
        return self.flashObject.as_updateBurnout(value) if self._isDAAPIInited() else None

    def as_addSpeedometerS(self, maxSpeedNormalMode, maxSpeedSpeedMode):
        return self.flashObject.as_addSpeedometer(maxSpeedNormalMode, maxSpeedSpeedMode) if self._isDAAPIInited() else None

    def as_removeSpeedometerS(self):
        return self.flashObject.as_removeSpeedometer() if self._isDAAPIInited() else None

    def as_setBurnoutWarningS(self, value):
        return self.flashObject.as_setBurnoutWarning(value) if self._isDAAPIInited() else None

    def as_stopBurnoutWarningS(self):
        return self.flashObject.as_stopBurnoutWarning() if self._isDAAPIInited() else None

    def as_setEngineCrushErrorS(self, value):
        return self.flashObject.as_setEngineCrushError(value) if self._isDAAPIInited() else None

    def as_stopEngineCrushErrorS(self):
        return self.flashObject.as_stopEngineCrushError() if self._isDAAPIInited() else None

    def as_startDualGunChargingS(self, timeLeft, totalTime):
        return self.flashObject.as_startDualGunCharging(timeLeft, totalTime) if self._isDAAPIInited() else None

    def as_cancelDualGunChargeS(self):
        return self.flashObject.as_cancelDualGunCharge() if self._isDAAPIInited() else None

    def as_updateDualGunMarkerStateS(self, markerState):
        return self.flashObject.as_updateDualGunMarkerState(markerState) if self._isDAAPIInited() else None

    def as_runCameraTransitionFxS(self, activeGunId, animationDuration):
        return self.flashObject.as_runCameraTransitionFx(activeGunId, animationDuration) if self._isDAAPIInited() else None

    def as_updateScaleWidgetS(self, positionValue):
        return self.flashObject.as_updateScaleWidget(positionValue) if self._isDAAPIInited() else None

    def as_setGunMarkersIndicatorsS(self, indicators):
        return self.flashObject.as_setGunMarkersIndicators(indicators) if self._isDAAPIInited() else None

    def as_setShotFlyTimesS(self, shotFlyTimes):
        return self.flashObject.as_setShotFlyTimes(shotFlyTimes) if self._isDAAPIInited() else None

    def as_setShellChangeTimeS(self, quickChangerIsActive, shellChangeTime):
        return self.flashObject.as_setShellChangeTime(quickChangerIsActive, shellChangeTime) if self._isDAAPIInited() else None

    def as_isFadedS(self, value):
        return self.flashObject.as_isFaded(value) if self._isDAAPIInited() else None

    def as_blinkReloadTimeS(self, blinkType):
        return self.flashObject.as_blinkReloadTime(blinkType) if self._isDAAPIInited() else None

    def as_setOverheatProgressS(self, value, isOverheated):
        return self.flashObject.as_setOverheatProgress(value, isOverheated) if self._isDAAPIInited() else None

    def as_addOverheatS(self, overheatMark):
        return self.flashObject.as_addOverheat(overheatMark) if self._isDAAPIInited() else None

    def as_removeOverheatS(self):
        return self.flashObject.as_removeOverheat() if self._isDAAPIInited() else None
