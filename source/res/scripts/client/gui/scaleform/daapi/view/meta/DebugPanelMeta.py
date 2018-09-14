# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DebugPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class DebugPanelMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def as_updatePingInfoS(self, pingValue):
        """
        :param pingValue:
        :return :
        """
        return self.flashObject.as_updatePingInfo(pingValue) if self._isDAAPIInited() else None

    def as_updateFPSInfoS(self, fpsValue):
        """
        :param fpsValue:
        :return :
        """
        return self.flashObject.as_updateFPSInfo(fpsValue) if self._isDAAPIInited() else None

    def as_updateLagInfoS(self, isLagging):
        """
        :param isLagging:
        :return :
        """
        return self.flashObject.as_updateLagInfo(isLagging) if self._isDAAPIInited() else None

    def as_updatePingFPSInfoS(self, pingValue, fpsValue):
        """
        :param pingValue:
        :param fpsValue:
        :return :
        """
        return self.flashObject.as_updatePingFPSInfo(pingValue, fpsValue) if self._isDAAPIInited() else None

    def as_updatePingFPSLagInfoS(self, pingValue, fpsValue, isLagging):
        """
        :param pingValue:
        :param fpsValue:
        :param isLagging:
        :return :
        """
        return self.flashObject.as_updatePingFPSLagInfo(pingValue, fpsValue, isLagging) if self._isDAAPIInited() else None
