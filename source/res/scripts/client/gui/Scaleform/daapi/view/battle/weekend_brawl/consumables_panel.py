# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/weekend_brawl/consumables_panel.py
import logging
from gui.battle_control.controllers.consumables.equipment_ctrl import isDynamicEquipment
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel, EMPTY_EQUIPMENT_TOOLTIP, ANIMATION_TYPES
_logger = logging.getLogger(__name__)

class WeekendBrawlConsumablesPanel(ConsumablesPanel):
    _DYNAMIC_EQUIPMENT_START_IDX = 6
    _DYNAMIC_EQUIPMENT_END_IDX = 6
    _ORDERS_START_IDX = 7

    def __init__(self):
        super(WeekendBrawlConsumablesPanel, self).__init__()
        self.__dynamicEquipmentRange = xrange(self._DYNAMIC_EQUIPMENT_START_IDX, self._DYNAMIC_EQUIPMENT_END_IDX + 1)
        self.__dynamicEquipmentFullMask = sum([ 1 << idx for idx in self.__dynamicEquipmentRange ])

    def _populate(self):
        super(WeekendBrawlConsumablesPanel, self)._populate()
        self.__addDynamicSlots()

    def _addListeners(self):
        super(WeekendBrawlConsumablesPanel, self)._addListeners()
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentRemoved += self.__onEquipmentRemoved
        return

    def _removeListeners(self):
        super(WeekendBrawlConsumablesPanel, self)._removeListeners()
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentRemoved -= self.__onEquipmentRemoved
        return

    def _onGunSettingsSet(self, _):
        super(WeekendBrawlConsumablesPanel, self)._onGunSettingsSet(_)
        self.__addDynamicSlots()

    def _onEquipmentAdded(self, intCD, item):
        if item is not None and isDynamicEquipment(item):
            if item.getQuantity() > 0:
                idx = self._genNextIdx(self.__dynamicEquipmentFullMask, self._DYNAMIC_EQUIPMENT_START_IDX)
                super(WeekendBrawlConsumablesPanel, self)._addEquipmentSlot(idx, intCD, item)
        else:
            super(WeekendBrawlConsumablesPanel, self)._onEquipmentAdded(intCD, item)
        return

    def _onEquipmentUpdated(self, intCD, item):
        if intCD in self._cds:
            self._updateEquipmentSlot(self._cds.index(intCD), item)

    def __onEquipmentRemoved(self, intCD, _):
        if intCD not in self._cds:
            _logger.debug('Equipment with cd=%d is not found in panel=%s', intCD, str(self._cds))
            return
        idx = self._cds.index(intCD)
        self._clearEquipmentGlowCallback(idx)
        self.__resetDynamicSlot(idx)

    def _onMappingChanged(self, *args):
        super(WeekendBrawlConsumablesPanel, self)._onMappingChanged(*args)
        slots = []
        for idx in self.__dynamicEquipmentRange:
            if self._cds[idx] is None:
                bwKey, sfKey = self._genKey(idx)
                slots.append((idx, bwKey, sfKey))

        if slots:
            self.as_setKeysToSlotsS(slots)
        return

    def _setEquipmentData(self, item, idx, bwKey, sfKey, quantity, timeRemaining, reloadingTime, iconPath, toolTip, animationType):
        if isDynamicEquipment(item):
            self.as_updateEquipmentSlotS(idx, bwKey, sfKey, quantity, timeRemaining, reloadingTime, iconPath, toolTip, animationType)
        else:
            self.as_addEquipmentSlotS(idx, bwKey, sfKey, quantity, timeRemaining, reloadingTime, iconPath, toolTip, animationType)

    def _isEquipmentWithKey(self, idx):
        return super(WeekendBrawlConsumablesPanel, self)._isEquipmentWithKey(idx) or idx in self.__dynamicEquipmentRange

    def __addDynamicSlots(self):
        for idx in self.__dynamicEquipmentRange:
            self.__addEmptySlot(idx)

    def __addEmptySlot(self, idx):
        self._cds[idx] = None
        bwKey, sfKey = self._genKey(idx)
        self.as_addEquipmentSlotS(idx, bwKey, sfKey, 0, 0, 0, None, EMPTY_EQUIPMENT_TOOLTIP, ANIMATION_TYPES.NONE, isAlwaysVisible=True)
        return

    def __resetDynamicSlots(self):
        for idx in self.__dynamicEquipmentRange:
            self.__resetDynamicSlot(idx)

    def __resetDynamicSlot(self, idx):
        self._mask &= ~(1 << idx)
        self._cds[idx] = None
        bwKey, sfKey = self._genKey(idx)
        self._resetBwKey(bwKey)
        self.as_updateEquipmentSlotS(idx, bwKey, sfKey, 0, 0, 0, '', EMPTY_EQUIPMENT_TOOLTIP, ANIMATION_TYPES.NONE)
        return
