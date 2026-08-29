# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/meta/WTConsumablesPanelMeta.py
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel

class WTConsumablesPanelMeta(ConsumablesPanel):

    def as_wtShowActiveS(self, idx, time=0):
        return self.flashObject.as_wtShowActive(idx, time) if self._isDAAPIInited() else None

    def as_wtSetDisabledS(self, idx, value):
        return self.flashObject.as_wtSetDisabled(idx, value) if self._isDAAPIInited() else None

    def as_wtShowCooldownS(self, idx, time):
        return self.flashObject.as_wtShowCooldown(idx, time) if self._isDAAPIInited() else None

    def as_wtShowReadyS(self, idx):
        return self.flashObject.as_wtShowReady(idx) if self._isDAAPIInited() else None

    def as_wtSetChargeProgressS(self, idx, charge):
        return self.flashObject.as_wtSetChargeProgress(idx, charge) if self._isDAAPIInited() else None

    def as_wtShowPreparingS(self, idx):
        return self.flashObject.as_wtShowPreparing(idx) if self._isDAAPIInited() else None

    def as_wtShowDeployingS(self, idx):
        return self.flashObject.as_wtShowDeploying(idx) if self._isDAAPIInited() else None

    def as_wtSetLockedS(self, idx, value):
        return self.flashObject.as_wtSetLocked(idx, value) if self._isDAAPIInited() else None

    def as_wtAddPassiveAbilitySlotS(self, idx, iconPath, tooltipText):
        return self.flashObject.as_wtAddPassiveAbilitySlot(idx, iconPath, tooltipText) if self._isDAAPIInited() else None
