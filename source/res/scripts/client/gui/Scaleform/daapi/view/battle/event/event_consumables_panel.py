# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_consumables_panel.py
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel

class EventConsumablesPanel(ConsumablesPanel):

    def _addEquipmentSlot(self, idx, intCD, item):
        if item is None:
            return
        else:
            super(EventConsumablesPanel, self)._addEquipmentSlot(idx, intCD, item)
            return
