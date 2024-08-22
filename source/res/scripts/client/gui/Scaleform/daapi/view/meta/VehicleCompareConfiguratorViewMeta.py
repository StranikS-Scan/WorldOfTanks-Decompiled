# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleCompareConfiguratorViewMeta.py
from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_configurator_base import VehicleCompareConfiguratorBaseView

class VehicleCompareConfiguratorViewMeta(VehicleCompareConfiguratorBaseView):

    def removeDevice(self, slotType, slotIndex):
        self._printOverrideError('removeDevice')

    def selectShell(self, shellId, slotIndex):
        self._printOverrideError('selectShell')

    def camoSelected(self, selected):
        self._printOverrideError('camoSelected')

    def showModules(self):
        self._printOverrideError('showModules')

    def toggleTopModules(self, value):
        self._printOverrideError('toggleTopModules')

    def as_setDevicesDataS(self, data):
        return self.flashObject.as_setDevicesData(data) if self._isDAAPIInited() else None

    def as_setAmmoS(self, shells):
        return self.flashObject.as_setAmmo(shells) if self._isDAAPIInited() else None

    def as_setSelectedAmmoIndexS(self, index):
        return self.flashObject.as_setSelectedAmmoIndex(index) if self._isDAAPIInited() else None

    def as_setCamoS(self, selected):
        return self.flashObject.as_setCamo(selected) if self._isDAAPIInited() else None

    def as_disableCamoS(self):
        return self.flashObject.as_disableCamo() if self._isDAAPIInited() else None

    def as_setTopModulesSelectedS(self, value):
        return self.flashObject.as_setTopModulesSelected(value) if self._isDAAPIInited() else None

    def as_setIsPostProgressionEnabledS(self, value):
        return self.flashObject.as_setIsPostProgressionEnabled(value) if self._isDAAPIInited() else None
