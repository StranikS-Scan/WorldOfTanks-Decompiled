# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/battle_royale/consumables_panel.py
from constants import EQUIPMENT_STAGES
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from gui.battle_royale.constants import AVATAR_EQUIPMENTS
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS

class BattleRoyaleConsumablesPanel(ConsumablesPanel):
    _PANEL_MAX_LENGTH = 10
    _AMMO_START_IDX = 0
    _AMMO_END_IDX = 1
    _AMMO_BITS_COUNT = _AMMO_END_IDX + 1
    _EQUIPMENT_START_IDX = 2
    _EQUIPMENT_END_IDX = 5
    _ORDERS_START_IDX = 6
    _ORDERS_END_IDX = 9
    _OPT_DEVICE_START_IDX = 10
    _OPT_DEVICE_END_IDX = 11
    __NUM_SHELL_SLOTS = _AMMO_END_IDX - _AMMO_START_IDX + 1
    __NUM_EQUIPMENT_SLOTS = _ORDERS_END_IDX - _EQUIPMENT_START_IDX + 1
    _EQUIPMENT_ICON_PATH = '../maps/icons/battleRoyale/artefact/%s.png'

    def __init__(self):
        super(BattleRoyaleConsumablesPanel, self).__init__()
        self.__quantityMap = [0] * self._PANEL_MAX_LENGTH

    def as_resetS(self):
        pass

    def _getPanelSettings(self):
        return CONSUMABLES_PANEL_SETTINGS.BATTLE_ROYALE_SETTINGS_ID

    def _onShellsAdded(self, intCD, descriptor, quantity, _, gunSettings):
        if self.__isAmmoMaskFilled():
            self.__updateMask()
        super(BattleRoyaleConsumablesPanel, self)._onShellsAdded(intCD, descriptor, quantity, _, gunSettings)

    def _addShellSlot(self, idx, intCD, descriptor, quantity, gunSettings):
        super(BattleRoyaleConsumablesPanel, self)._addShellSlot(idx, intCD, descriptor, quantity, gunSettings)
        self.__quantityMap[idx] = quantity

    def _addEquipmentSlot(self, idx, intCD, item=None):
        if self._cds is not None and self._cds[idx] is not None:
            return
        else:
            super(BattleRoyaleConsumablesPanel, self)._addEquipmentSlot(idx, intCD, item)
            quantity = item.getQuantity() if item is not None else 0
            self.__quantityMap[idx] = quantity
            return

    def _onEquipmentAdded(self, intCD, item):
        if intCD in self._cds:
            return
        super(BattleRoyaleConsumablesPanel, self)._onEquipmentAdded(intCD, item)

    def _isAvatarEquipment(self, item):
        return item.getDescriptor().name in AVATAR_EQUIPMENTS

    def _addOptionalDeviceSlot(self, idx, intCD, descriptor, isActive):
        pass

    def _updateShellSlot(self, idx, quantity):
        super(BattleRoyaleConsumablesPanel, self)._updateShellSlot(idx, quantity)
        if quantity > self.__quantityMap[idx]:
            self.as_setGlowS(idx, CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN)
        self.__quantityMap[idx] = quantity

    def _updateEquipmentSlot(self, idx, item):
        super(BattleRoyaleConsumablesPanel, self)._updateEquipmentSlot(idx, item)
        quantity = item.getQuantity()
        if quantity != self.__quantityMap[idx]:
            if quantity > self.__quantityMap[idx]:
                self.as_setGlowS(idx, CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN)
            elif item.getPrevStage() == EQUIPMENT_STAGES.ACTIVE:
                self.as_setGlowS(idx, CONSUMABLES_PANEL_SETTINGS.GLOW_ID_ORANGE)
            self.__quantityMap[idx] = quantity
        if item.becomeReady and item.getPrevStage() != EQUIPMENT_STAGES.DEPLOYING and quantity != 0:
            self.as_setGlowS(idx, CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_SPECIAL)

    def _updateOptionalDeviceSlot(self, idx, isOn):
        pass

    def _showEquipmentGlow(self, equipmentIndex, glowType=CONSUMABLES_PANEL_SETTINGS.GLOW_ID_ORANGE):
        pass

    def __isAmmoMaskFilled(self):
        lastAmmoShellBit = 1
        lastAmmoShellBit <<= self._AMMO_END_IDX
        lastAmmoShellBit &= self._mask
        return lastAmmoShellBit

    def __updateMask(self):
        self._mask >>= self._AMMO_BITS_COUNT
        self._mask <<= self._AMMO_BITS_COUNT

    def _resetCds(self):
        for idx in range(self._AMMO_START_IDX, self._AMMO_END_IDX + 1):
            self._cds[idx] = None

        return

    def _onGunSettingsSet(self, _):
        self._resetCds()
