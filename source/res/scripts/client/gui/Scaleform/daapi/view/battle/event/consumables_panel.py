# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/consumables_panel.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items import getKpiValueString
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel

class EventConsumablesPanel(ConsumablesPanel):
    _AMMO_START_IDX = 0
    _AMMO_END_IDX = 0
    _EQUIPMENT_START_IDX = 1
    _EQUIPMENT_END_IDX = 6
    _ORDERS_START_IDX = 8
    _ORDERS_END_IDX = 8

    def __init__(self):
        super(EventConsumablesPanel, self).__init__()
        self.__lockedStateEquipments = list()

    def _dispose(self):
        self.__lockedStateEquipments = list()
        super(EventConsumablesPanel, self)._dispose()

    def _addListeners(self):
        super(EventConsumablesPanel, self)._addListeners()
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentStateLocked += self.__onEquipmentStateLocked
            eqCtrl.onEquipmentStateUnlocked += self.__onEquipmentStateUnlocked
        return

    def _removeListeners(self):
        super(EventConsumablesPanel, self)._removeListeners()
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentStateLocked -= self.__onEquipmentStateLocked
            eqCtrl.onEquipmentStateUnlocked -= self.__onEquipmentStateUnlocked
        return

    def _isNeedsExtendTooltipBody(self, item):
        return not {'repairkit', 'medkit'} & item.getDescriptor().tags

    def _getAdditionalTooltipBodyString(self, item):
        attribs = R.strings.artefacts.dyn(item.getDescriptor().name)
        if not attribs:
            return ''
        resultStr = ''
        emptyStr = backport.text(R.strings.artefacts.empty())
        kpiArgs = {kpi.name:getKpiValueString(kpi, kpi.value) for kpi in item.getDescriptor().kpi}
        attributes = ('onUse', 'always', 'restriction')
        for atr in attributes:
            strText = backport.text(getattr(attribs, atr)(), **kpiArgs)
            if strText and strText != emptyStr:
                eq = R.strings.tooltips.equipment
                description = text_styles.middleTitle(backport.text(getattr(eq, atr)()))
                block = '\n'.join((description, strText))
                resultStr = '\n\n'.join((resultStr, block))

        return resultStr

    def __onEquipmentStateLocked(self, intCD):
        self.__lockedStateEquipments.append(intCD)

    def __onEquipmentStateUnlocked(self, intCD):
        self.__lockedStateEquipments.remove(intCD)

    def _updateEquipmentSlot(self, idx, item):
        intCD = self._cds[idx]
        if intCD in self.__lockedStateEquipments:
            return
        super(EventConsumablesPanel, self)._updateEquipmentSlot(idx, item)
