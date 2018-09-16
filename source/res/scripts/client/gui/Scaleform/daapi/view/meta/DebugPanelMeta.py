# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DebugPanelMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class DebugPanelMeta(BaseDAAPIComponent):

    def as_updatePingInfoS(self, pingValue):
        return self.flashObject.as_updatePingInfo(pingValue) if self._isDAAPIInited() else None

    def as_updateFPSInfoS(self, fpsValue):
        return self.flashObject.as_updateFPSInfo(fpsValue) if self._isDAAPIInited() else None

    def as_updateLagInfoS(self, isLagging):
        return self.flashObject.as_updateLagInfo(isLagging) if self._isDAAPIInited() else None

    def as_updatePingFPSInfoS(self, pingValue, fpsValue):
        return self.flashObject.as_updatePingFPSInfo(pingValue, fpsValue) if self._isDAAPIInited() else None

    def as_updatePingFPSLagInfoS(self, pingValue, fpsValue, isLagging):
        return self.flashObject.as_updatePingFPSLagInfo(pingValue, fpsValue, isLagging) if self._isDAAPIInited() else None
