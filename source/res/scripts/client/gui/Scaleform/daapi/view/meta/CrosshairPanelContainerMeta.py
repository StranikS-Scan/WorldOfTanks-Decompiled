# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CrosshairPanelContainerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CrosshairPanelContainerMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def as_populateS(self):
        return self.flashObject.as_populate() if self._isDAAPIInited() else None

    def as_disposeS(self):
        return self.flashObject.as_dispose() if self._isDAAPIInited() else None

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

    def as_setHealthS(self, percent):
        return self.flashObject.as_setHealth(percent) if self._isDAAPIInited() else None

    def as_setAmmoStockS(self, quantity, quantityInClip, isLow, clipState, clipReloaded):
        return self.flashObject.as_setAmmoStock(quantity, quantityInClip, isLow, clipState, clipReloaded) if self._isDAAPIInited() else None

    def as_setClipParamsS(self, clipCapacity, burst):
        return self.flashObject.as_setClipParams(clipCapacity, burst) if self._isDAAPIInited() else None

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

    def as_setNetVisibleS(self, value):
        return self.flashObject.as_setNetVisible(value) if self._isDAAPIInited() else None

    def as_setNetTypeS(self, netType):
        return self.flashObject.as_setNetType(netType) if self._isDAAPIInited() else None

    def as_showHintS(self, key, messageLeft, messageRight, offsetX, offsetY):
        return self.flashObject.as_showHint(key, messageLeft, messageRight, offsetX, offsetY) if self._isDAAPIInited() else None

    def as_hideHintS(self):
        return self.flashObject.as_hideHint() if self._isDAAPIInited() else None
