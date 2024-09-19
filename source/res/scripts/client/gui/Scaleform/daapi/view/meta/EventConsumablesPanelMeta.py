# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventConsumablesPanelMeta.py
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel

class EventConsumablesPanelMeta(ConsumablesPanel):

    def as_setChargeProgressS(self, idx, charge, isVisible):
        return self.flashObject.as_setChargeProgress(idx, charge, isVisible) if self._isDAAPIInited() else None

    def as_setSelectedS(self, idx, isSelected):
        return self.flashObject.as_setSelected(idx, isSelected) if self._isDAAPIInited() else None

    def as_setDebuffViewS(self, idx, isDebuffMode):
        return self.flashObject.as_setDebuffView(idx, isDebuffMode) if self._isDAAPIInited() else None

    def as_setInspiredS(self, isInspired):
        return self.flashObject.as_setInspired(isInspired) if self._isDAAPIInited() else None
