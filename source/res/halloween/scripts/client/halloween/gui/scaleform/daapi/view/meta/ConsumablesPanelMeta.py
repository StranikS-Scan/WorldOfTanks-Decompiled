# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/meta/ConsumablesPanelMeta.py
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel

class ConsumablesPanelMeta(ConsumablesPanel):

    def as_addAbilitySlotS(self, idx, keyCode, sfKeyCode, quantity, timeRemaining, reloadingTime, iconPath, tooltipText):
        return self.flashObject.as_addAbilitySlot(idx, keyCode, sfKeyCode, quantity, timeRemaining, reloadingTime, iconPath, tooltipText) if self._isDAAPIInited() else None

    def as_updateAbilityS(self, idx, stage, count, timeRemaining, maxTime):
        return self.flashObject.as_updateAbility(idx, stage, count, timeRemaining, maxTime) if self._isDAAPIInited() else None

    def as_addPassiveAbilitySlotS(self, idx, iconPath, state, tooltipText):
        return self.flashObject.as_addPassiveAbilitySlot(idx, iconPath, state, tooltipText) if self._isDAAPIInited() else None

    def as_updatePassiveAbilityS(self, idx, iconPath, state, tooltipText):
        return self.flashObject.as_updatePassiveAbility(idx, iconPath, state, tooltipText) if self._isDAAPIInited() else None

    def as_resetPassiveAbilitiesS(self, slots=None):
        return self.flashObject.as_resetPassiveAbilities(slots) if self._isDAAPIInited() else None
