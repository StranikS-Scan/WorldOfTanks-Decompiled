# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleCompareConfiguratorViewMeta.py
from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_configurator_base import VehicleCompareConfiguratorBaseView

class VehicleCompareConfiguratorViewMeta(VehicleCompareConfiguratorBaseView):

    def removeDevice(self, slotType, slotIndex):
        self._printOverrideError('removeDevice')

    def showModules(self):
        self._printOverrideError('showModules')

    def toggleTopModules(self, value):
        self._printOverrideError('toggleTopModules')

    def as_setDevicesDataS(self, data):
        return self.flashObject.as_setDevicesData(data) if self._isDAAPIInited() else None

    def as_setTopModulesSelectedS(self, value):
        return self.flashObject.as_setTopModulesSelected(value) if self._isDAAPIInited() else None

    def as_setDetachmentHeightS(self, value):
        return self.flashObject.as_setDetachmentHeight(value) if self._isDAAPIInited() else None
