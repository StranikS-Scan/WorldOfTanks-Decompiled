# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_consumables_panel.py
import logging
import CommandMapping
from constants import EVENT
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS
from gui.shared.utils.key_mapping import getScaleformKey
_logger = logging.getLogger(__name__)

class EventConsumablesPanel(ConsumablesPanel):
    _ORDERS_START_IDX = 7
    _NITRO_START_IDX = _ORDERS_START_IDX - 1
    _NITRO_MASK = 1 << _NITRO_START_IDX

    def __init__(self):
        super(EventConsumablesPanel, self).__init__()
        self._shellCount = {}

    def _resetCds(self):
        super(EventConsumablesPanel, self)._resetCds()
        self._shellCount = {}

    def _addEquipmentSlot(self, idx, intCD, item):
        if item is None:
            return
        else:
            super(EventConsumablesPanel, self)._addEquipmentSlot(idx, intCD, item)
            return

    def _genKey(self, idx):
        if idx == self._NITRO_START_IDX:
            cmdMap = CommandMapping.g_instance
            bwKey, _ = cmdMap.getCommandKeys(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
            sfKey = getScaleformKey(bwKey)
            return (bwKey, sfKey)
        return super(EventConsumablesPanel, self)._genKey(idx)

    def _onEquipmentAdded(self, intCD, item):
        if item is not None and not self._isAvatarEquipment(item):
            descriptor = item.getDescriptor()
            if descriptor.name.startswith(EVENT.NITRO_BUILTIN_EXTRA_PATTERN):
                bits = self._mask & self._NITRO_MASK
                if bits == 0:
                    idx = self._ConsumablesPanel__genNextIdx(self._NITRO_MASK, self._NITRO_START_IDX)
                    self._addEquipmentSlot(idx, intCD, item)
                else:
                    _logger.info('The vehicle already has a nitro consumable')
                return
        super(EventConsumablesPanel, self)._onEquipmentAdded(intCD, item)
        return

    def _onShellsAdded(self, intCD, descriptor, quantity, *args):
        super(EventConsumablesPanel, self)._onShellsAdded(intCD, descriptor, quantity, *args)
        self._shellCount[intCD] = quantity

    def _onShellsUpdated(self, intCD, quantity, *args):
        super(EventConsumablesPanel, self)._onShellsUpdated(intCD, quantity, *args)
        if intCD not in self._cds:
            return
        prevCount = self._shellCount.get(intCD, 0)
        if quantity > prevCount:
            idx = self._cds.index(intCD)
            self.as_setGlowS(idx, CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_SPECIAL)
        if quantity != prevCount:
            self._shellCount[intCD] = quantity

    def _isIdxInKeysRange(self, idx):
        return super(EventConsumablesPanel, self)._isIdxInKeysRange(idx) or idx == self._NITRO_START_IDX
