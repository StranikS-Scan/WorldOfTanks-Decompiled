# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicBattleConsumablesPanelMeta.py
from gui.Scaleform.daapi.view.meta.ConsumablesPanelMeta import ConsumablesPanelMeta

class EpicBattleConsumablesPanelMeta(ConsumablesPanelMeta):

    def as_addEpicBattleEquipmentSlotS(self, idx, keyCode, sfKeyCode, quantity, timeRemaining, reloadingTime, iconPath, isTooltipSpecial, tooltipText, animation):
        return self.flashObject.as_addEpicBattleEquipmentSlot(idx, keyCode, sfKeyCode, quantity, timeRemaining, reloadingTime, iconPath, isTooltipSpecial, tooltipText, animation) if self._isDAAPIInited() else None

    def as_updateLockedInformationS(self, idx, lockedID, tooltipStr, isSlotEmpty):
        return self.flashObject.as_updateLockedInformation(idx, lockedID, tooltipStr, isSlotEmpty) if self._isDAAPIInited() else None

    def as_updateLevelInformationS(self, idx, level):
        return self.flashObject.as_updateLevelInformation(idx, level) if self._isDAAPIInited() else None

    def as_showPossibleStacksS(self, idx, stack):
        return self.flashObject.as_showPossibleStacks(idx, stack) if self._isDAAPIInited() else None

    def as_updateStacksS(self, idx, stack):
        return self.flashObject.as_updateStacks(idx, stack) if self._isDAAPIInited() else None
