# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AmmunitionPanelMeta.py
from gui.Scaleform.daapi.view.meta.ModulesPanelMeta import ModulesPanelMeta

class AmmunitionPanelMeta(ModulesPanelMeta):

    def showTechnicalMaintenance(self):
        self._printOverrideError('showTechnicalMaintenance')

    def showCustomization(self):
        self._printOverrideError('showCustomization')

    def toRentContinue(self):
        self._printOverrideError('toRentContinue')

    def showChangeNation(self):
        self._printOverrideError('showChangeNation')

    def toggleNYCustomization(self, selected):
        self._printOverrideError('toggleNYCustomization')

    def onNYBonusPanelClicked(self):
        self._printOverrideError('onNYBonusPanelClicked')

    def as_setAmmoS(self, shells, stateWarning):
        return self.flashObject.as_setAmmo(shells, stateWarning) if self._isDAAPIInited() else None

    def as_updateVehicleStatusS(self, data):
        return self.flashObject.as_updateVehicleStatus(data) if self._isDAAPIInited() else None

    def as_showBattleAbilitiesAlertS(self, value):
        return self.flashObject.as_showBattleAbilitiesAlert(value) if self._isDAAPIInited() else None

    def as_setCustomizationBtnCounterS(self, value):
        return self.flashObject.as_setCustomizationBtnCounter(value) if self._isDAAPIInited() else None

    def as_setBoosterBtnCounterS(self, value):
        return self.flashObject.as_setBoosterBtnCounter(value) if self._isDAAPIInited() else None

    def as_setNeyYearVehicleBonusS(self, enabled, bonusIcon, bonusValue, label, nyBranchTooltip):
        return self.flashObject.as_setNeyYearVehicleBonus(enabled, bonusIcon, bonusValue, label, nyBranchTooltip) if self._isDAAPIInited() else None

    def as_setNYCustomizationSlotStateS(self, selected, enabled):
        return self.flashObject.as_setNYCustomizationSlotState(selected, enabled) if self._isDAAPIInited() else None
