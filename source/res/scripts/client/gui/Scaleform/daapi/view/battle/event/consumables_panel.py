# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/consumables_panel.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items import getKpiValueString
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel, TOOLTIP_FORMAT

class EventConsumablesPanel(ConsumablesPanel):
    _AMMO_START_IDX = 0
    _AMMO_END_IDX = 0
    _EQUIPMENT_START_IDX = 1
    _EQUIPMENT_END_IDX = 6
    _ORDERS_START_IDX = 8
    _ORDERS_END_IDX = 8

    def _buildEquipmentSlotTooltipText(self, item):
        descriptor = item.getDescriptor()
        reloadingTime = descriptor.cooldownSeconds
        body = descriptor.description
        if not {'repairkit', 'medkit'} & descriptor.tags:
            additionalStr = self.__getAdditionalTooltipBodyString(item)
            body = ''.join((body, additionalStr))
        if reloadingTime > 0:
            tooltipStr = R.strings.ingame_gui.consumables_panel.equipment.cooldownSeconds()
            cooldownSeconds = str(int(reloadingTime))
            paramsString = backport.text(tooltipStr, cooldownSeconds=cooldownSeconds)
            body = '\n\n'.join((body, paramsString))
        toolTip = TOOLTIP_FORMAT.format(descriptor.userString, body)
        return toolTip

    def __getAdditionalTooltipBodyString(self, item):
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
