# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AmmunitionPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class AmmunitionPanelMeta(BaseDAAPIComponent):

    def showRepairDialog(self):
        self._printOverrideError('showRepairDialog')

    def showCustomization(self):
        self._printOverrideError('showCustomization')

    def toRentContinue(self):
        self._printOverrideError('toRentContinue')

    def showChangeNation(self):
        self._printOverrideError('showChangeNation')

    def showEasyTankEquip(self):
        self._printOverrideError('showEasyTankEquip')

    def as_setMaintenanceWarningStateS(self, stateWarning):
        return self.flashObject.as_setMaintenanceWarningState(stateWarning) if self._isDAAPIInited() else None

    def as_highlightEasyTankEquipS(self, isHighlight):
        return self.flashObject.as_highlightEasyTankEquip(isHighlight) if self._isDAAPIInited() else None

    def as_updateVehicleStatusS(self, data):
        return self.flashObject.as_updateVehicleStatus(data) if self._isDAAPIInited() else None

    def as_setCustomizationBtnCounterS(self, value):
        return self.flashObject.as_setCustomizationBtnCounter(value) if self._isDAAPIInited() else None
