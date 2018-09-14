# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AmmunitionPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class AmmunitionPanelMeta(BaseDAAPIComponent):

    def setVehicleModule(self, newId, slotIdx, oldId, isRemove):
        self._printOverrideError('setVehicleModule')

    def showModuleInfo(self, moduleId):
        self._printOverrideError('showModuleInfo')

    def showTechnicalMaintenance(self):
        self._printOverrideError('showTechnicalMaintenance')

    def showCustomization(self):
        self._printOverrideError('showCustomization')

    def highlightParams(self, type):
        self._printOverrideError('highlightParams')

    def toRentContinue(self):
        self._printOverrideError('toRentContinue')

    def as_setDataS(self, devices):
        return self.flashObject.as_setData(devices) if self._isDAAPIInited() else None

    def as_setAmmoS(self, shells, stateWarning):
        return self.flashObject.as_setAmmo(shells, stateWarning) if self._isDAAPIInited() else None

    def as_setVehicleHasTurretS(self, hasTurret):
        return self.flashObject.as_setVehicleHasTurret(hasTurret) if self._isDAAPIInited() else None

    def as_setModulesEnabledS(self, value):
        return self.flashObject.as_setModulesEnabled(value) if self._isDAAPIInited() else None

    def as_updateVehicleStatusS(self, data):
        return self.flashObject.as_updateVehicleStatus(data) if self._isDAAPIInited() else None
