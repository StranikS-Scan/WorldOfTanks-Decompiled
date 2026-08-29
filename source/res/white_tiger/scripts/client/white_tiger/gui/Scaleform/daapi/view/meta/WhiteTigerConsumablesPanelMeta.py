# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/meta/WhiteTigerConsumablesPanelMeta.py
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel

class WhiteTigerConsumablesPanelMeta(ConsumablesPanel):

    def as_setChargeProgressS(self, idx, charge, isVisible):
        return self.flashObject.as_setChargeProgress(idx, charge, isVisible) if self._isDAAPIInited() else None

    def as_setSelectedS(self, idx, isSelected):
        return self.flashObject.as_setSelected(idx, isSelected) if self._isDAAPIInited() else None

    def as_setDebuffViewS(self, idx, isDebuffMode):
        return self.flashObject.as_setDebuffView(idx, isDebuffMode) if self._isDAAPIInited() else None

    def as_setInspiredS(self, isInspired):
        return self.flashObject.as_setInspired(isInspired) if self._isDAAPIInited() else None

    def as_addWhiteTigerEquipmentSlotS(self, idx, keyCode, sfKeyCode, quantity, timeRemaining, reloadingTime, iconPath, tooltipText, animation, tag, stage):
        return self.flashObject.as_addWhiteTigerEquipmentSlot(idx, keyCode, sfKeyCode, quantity, timeRemaining, reloadingTime, iconPath, tooltipText, animation, tag, stage) if self._isDAAPIInited() else None

    def as_setStageS(self, idx, stage):
        return self.flashObject.as_setStage(idx, stage) if self._isDAAPIInited() else None
