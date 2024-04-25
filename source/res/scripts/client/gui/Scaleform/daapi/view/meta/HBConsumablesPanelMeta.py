# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HBConsumablesPanelMeta.py
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel

class HBConsumablesPanelMeta(ConsumablesPanel):

    def as_setShellInfinityS(self, idx, value):
        return self.flashObject.as_setShellInfinity(idx, value) if self._isDAAPIInited() else None

    def as_addAbilitySlotS(self, idx, keyCode, sfKeyCode, quantity, timeRemaining, reloadingTime, iconPath, tooltipText):
        return self.flashObject.as_addAbilitySlot(idx, keyCode, sfKeyCode, quantity, timeRemaining, reloadingTime, iconPath, tooltipText) if self._isDAAPIInited() else None

    def as_updateAbilityS(self, idx, stage, timeRemaining, maxTime):
        return self.flashObject.as_updateAbility(idx, stage, timeRemaining, maxTime) if self._isDAAPIInited() else None

    def as_addPassiveAbilitySlotS(self, idx, iconPath, state, tooltipText):
        return self.flashObject.as_addPassiveAbilitySlot(idx, iconPath, state, tooltipText) if self._isDAAPIInited() else None

    def as_updatePassiveAbilityS(self, idx, state, tooltipText):
        return self.flashObject.as_updatePassiveAbility(idx, state, tooltipText) if self._isDAAPIInited() else None

    def as_resetPassiveAbilitiesS(self, slots=None):
        return self.flashObject.as_resetPassiveAbilities(slots) if self._isDAAPIInited() else None

    def as_addRoleAbilitySlotS(self, idx, keyCode, sfKeyCode, quantity, timeRemaining, reloadingTime, iconPath, tooltipText):
        return self.flashObject.as_addRoleAbilitySlot(idx, keyCode, sfKeyCode, quantity, timeRemaining, reloadingTime, iconPath, tooltipText) if self._isDAAPIInited() else None

    def as_setRoleAbilityProgressS(self, idx, progress=0):
        return self.flashObject.as_setRoleAbilityProgress(idx, progress) if self._isDAAPIInited() else None

    def as_setRoleAbilityTooltipS(self, idx, tooltipText):
        return self.flashObject.as_setRoleAbilityTooltip(idx, tooltipText) if self._isDAAPIInited() else None
