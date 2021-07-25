# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleParametersMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class VehicleParametersMeta(BaseDAAPIComponent):

    def onParamClick(self, paramID):
        self._printOverrideError('onParamClick')

    def onListScroll(self):
        self._printOverrideError('onListScroll')

    def as_getDPS(self):
        return self.flashObject.as_getDP() if self._isDAAPIInited() else None

    def as_setIsParamsAnimatedS(self, isParamsAnimated):
        return self.flashObject.as_setIsParamsAnimated(isParamsAnimated) if self._isDAAPIInited() else None

    def as_setDetachmentDataS(self, data):
        return self.flashObject.as_setDetachmentData(data) if self._isDAAPIInited() else None

    def as_setDetachmentVisibleS(self, visible):
        return self.flashObject.as_setDetachmentVisible(visible) if self._isDAAPIInited() else None
