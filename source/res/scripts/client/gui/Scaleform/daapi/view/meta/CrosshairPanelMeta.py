# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CrosshairPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CrosshairPanelMeta(BaseDAAPIComponent):
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

    def as_setViewS(self, view):
        return self.flashObject.as_setView(view) if self._isDAAPIInited() else None

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
