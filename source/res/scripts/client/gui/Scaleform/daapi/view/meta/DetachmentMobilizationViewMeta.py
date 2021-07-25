# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DetachmentMobilizationViewMeta.py
from gui.Scaleform.framework.entities.View import View

class DetachmentMobilizationViewMeta(View):

    def onEscapePress(self):
        self._printOverrideError('onEscapePress')

    def onEnterPress(self):
        self._printOverrideError('onEnterPress')

    def as_updateComponentPositionS(self, id, x, y, width, height):
        return self.flashObject.as_updateComponentPosition(id, x, y, width, height) if self._isDAAPIInited() else None

    def as_updateVehicleFilterButtonS(self, vehicleFilterVO):
        return self.flashObject.as_updateVehicleFilterButton(vehicleFilterVO) if self._isDAAPIInited() else None

    def as_setIsMedallionEnableS(self, isEnable):
        return self.flashObject.as_setIsMedallionEnable(isEnable) if self._isDAAPIInited() else None

    def as_setRecruitsEnabledS(self, value):
        return self.flashObject.as_setRecruitsEnabled(value) if self._isDAAPIInited() else None

    def as_setConversionStateS(self, state):
        return self.flashObject.as_setConversionState(state) if self._isDAAPIInited() else None
