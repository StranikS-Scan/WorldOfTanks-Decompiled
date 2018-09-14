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
        if self._isDAAPIInited():
            return self.flashObject.as_setData(devices)

    def as_setAmmoS(self, shells, stateWarning):
        if self._isDAAPIInited():
            return self.flashObject.as_setAmmo(shells, stateWarning)

    def as_setVehicleHasTurretS(self, hasTurret):
        if self._isDAAPIInited():
            return self.flashObject.as_setVehicleHasTurret(hasTurret)

    def as_setHistoricalBattleS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setHistoricalBattle(value)

    def as_setModulesEnabledS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setModulesEnabled(value)

    def as_updateVehicleStatusS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_updateVehicleStatus(data)
