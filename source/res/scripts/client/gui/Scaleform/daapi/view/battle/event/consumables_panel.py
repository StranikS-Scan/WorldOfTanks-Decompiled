# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/consumables_panel.py
from constants import EQUIPMENT_STAGES
from gui.Scaleform.daapi.view.meta.EventConsumablesPanelMeta import EventConsumablesPanelMeta
from gui.Scaleform.genConsts.ANIMATION_TYPES import ANIMATION_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items import getKpiValueString
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import TOOLTIP_FORMAT
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_WT_HYPERION_ITEM_NAME = 'builtinHyperion_wt'

class EventConsumablesPanel(EventConsumablesPanelMeta):
    _AMMO_START_IDX = 0
    _AMMO_END_IDX = 0
    _EQUIPMENT_START_IDX = 1
    _EQUIPMENT_END_IDX = 6
    _ORDERS_START_IDX = 8
    _ORDERS_END_IDX = 8
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EventConsumablesPanel, self).__init__()
        self._currentStage = EQUIPMENT_STAGES.UNAVAILABLE

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

    def _populate(self):
        super(EventConsumablesPanel, self)._populate()
        equipmentCtrl = self.sessionProvider.shared.equipments
        if equipmentCtrl is not None:
            equipmentCtrl.onChargeEquipmentCounterChanged += self.__onChargeCounterChanged
            equipmentCtrl.onDebuffEquipmentChanged += self.__onDebuffEquipmentChanged
        return

    def _dispose(self):
        super(EventConsumablesPanel, self)._dispose()
        equipmentCtrl = self.sessionProvider.shared.equipments
        if equipmentCtrl is not None:
            equipmentCtrl.onChargeEquipmentCounterChanged -= self.__onChargeCounterChanged
            equipmentCtrl.onDebuffEquipmentChanged -= self.__onDebuffEquipmentChanged
        return

    def _updateEquipmentSlot(self, idx, item):
        self._currentStage = item.getStage()
        if self._currentStage == EQUIPMENT_STAGES.COOLDOWN or self._currentStage == EQUIPMENT_STAGES.INTERRUPTED:
            if item.getDescriptor().name == _WT_HYPERION_ITEM_NAME:
                item.setAnimationType(ANIMATION_TYPES.SHOW_COUNTER_GREEN)
            else:
                item.setAnimationType(ANIMATION_TYPES.MOVE_ORANGE_BAR_UP | ANIMATION_TYPES.SHOW_COUNTER_ORANGE)
        elif self._currentStage == EQUIPMENT_STAGES.ACTIVE:
            item.setAnimationType(ANIMATION_TYPES.MOVE_GREEN_BAR_DOWN)
        super(EventConsumablesPanel, self)._updateEquipmentSlot(idx, item)
        if self._currentStage == EQUIPMENT_STAGES.EXHAUSTED:
            self.as_hideGlowS(idx)

    def _updateActivatedSlot(self, idx, item):
        self.as_setSelectedS(idx, self._currentStage == EQUIPMENT_STAGES.PREPARING)
        if self._currentStage == EQUIPMENT_STAGES.PREPARING:
            self.as_hideGlowS(idx)

    def __onChargeCounterChanged(self, intCD, charge, isVisible):
        if intCD not in self._cds:
            return
        idx = self._cds.index(intCD)
        self.as_setChargeProgressS(idx, charge, isVisible)

    def __onDebuffEquipmentChanged(self, intCD, isDebuffView):
        if intCD not in self._cds:
            return
        idx = self._cds.index(intCD)
        self.as_setDebuffViewS(idx, isDebuffView)
