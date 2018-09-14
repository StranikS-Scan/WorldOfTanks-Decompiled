# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CrosshairPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CrosshairPanelMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def as_populateS(self):
        """
        :return :
        """
        return self.flashObject.as_populate() if self._isDAAPIInited() else None

    def as_disposeS(self):
        """
        :return :
        """
        return self.flashObject.as_dispose() if self._isDAAPIInited() else None

    def as_setSettingsS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setSettings(data) if self._isDAAPIInited() else None

    def as_setViewS(self, view):
        """
        :param view:
        :return :
        """
        return self.flashObject.as_setView(view) if self._isDAAPIInited() else None

    def as_recreateDeviceS(self, offsetX, offsetY):
        """
        :param offsetX:
        :param offsetY:
        :return :
        """
        return self.flashObject.as_recreateDevice(offsetX, offsetY) if self._isDAAPIInited() else None

    def as_setReloadingCounterShownS(self, visible):
        """
        :param visible:
        :return :
        """
        return self.flashObject.as_setReloadingCounterShown(visible) if self._isDAAPIInited() else None

    def as_setReloadingS(self, duration, baseTime, startTime, isReloading):
        """
        :param duration:
        :param baseTime:
        :param startTime:
        :param isReloading:
        :return :
        """
        return self.flashObject.as_setReloading(duration, baseTime, startTime, isReloading) if self._isDAAPIInited() else None

    def as_setReloadingAsPercentS(self, percent, isReloading):
        """
        :param percent:
        :param isReloading:
        :return :
        """
        return self.flashObject.as_setReloadingAsPercent(percent, isReloading) if self._isDAAPIInited() else None

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

    def as_setDistanceS(self, dist):
        """
        :param dist:
        :return :
        """
        return self.flashObject.as_setDistance(dist) if self._isDAAPIInited() else None

    def as_clearDistanceS(self, immediate):
        """
        :param immediate:
        :return :
        """
        return self.flashObject.as_clearDistance(immediate) if self._isDAAPIInited() else None

    def as_updatePlayerInfoS(self, info):
        """
        :param info:
        :return :
        """
        return self.flashObject.as_updatePlayerInfo(info) if self._isDAAPIInited() else None

    def as_updateAmmoStateS(self, ammoState):
        """
        :param ammoState:
        :return :
        """
        return self.flashObject.as_updateAmmoState(ammoState) if self._isDAAPIInited() else None

    def as_setZoomS(self, zoomStr):
        """
        :param zoomStr:
        :return :
        """
        return self.flashObject.as_setZoom(zoomStr) if self._isDAAPIInited() else None
