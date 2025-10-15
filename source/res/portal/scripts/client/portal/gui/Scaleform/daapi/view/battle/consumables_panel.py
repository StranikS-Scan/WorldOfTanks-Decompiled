# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/consumables_panel.py
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel, TOOLTIP_FORMAT
from constants import EQUIPMENT_STAGES
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS
from gui.impl import backport
from gui.impl.gen import R
from items import vehicles, ITEM_TYPES
_ACTIVE_EQUIPMENT_STAGES = (EQUIPMENT_STAGES.PREPARING, EQUIPMENT_STAGES.ACTIVE)
_INACTIVE_EQUIPMENT_STAGES = (EQUIPMENT_STAGES.DEPLOYING,
 EQUIPMENT_STAGES.COOLDOWN,
 EQUIPMENT_STAGES.NOT_RUNNING,
 EQUIPMENT_STAGES.UNAVAILABLE)

class PortalConsumablesPanel(ConsumablesPanel):
    _EQUIPMENT_START_IDX = 0
    _EQUIPMENT_END_IDX = 2
    _BUILTIN_EQUIPMENT_START_IDX = 3
    _BUILTIN_EQUIPMENT_END_IDX = 5
    _AMMO_START_IDX = 6
    _AMMO_END_IDX = 8
    _REMAPPED_ICONS = {'largeRepairkit': 'large_repairkit_portal'}

    def __init__(self):
        super(PortalConsumablesPanel, self).__init__()
        self.__vehicleChangeComponent = getattr(BigWorld.player(), 'DynamicVehicleChangeComponent', None)
        self.__lastBuiltInEqIdx = self._BUILTIN_EQUIPMENT_START_IDX
        return

    def _dispose(self):
        self.__vehicleChangeComponent = None
        super(PortalConsumablesPanel, self)._dispose()
        return

    def _onEquipmentAdded(self, intCD, item):
        if item is None or intCD in self._cds:
            return
        else:
            slotIdx = 0
            itemTypeID, _, itemID = vehicles.parseIntCompactDescr(intCD)
            if itemTypeID == ITEM_TYPES.equipment:
                if self.__isPortalEquipment(item):
                    equipmentItem = vehicles.g_cache.equipments().get(itemID)
                    slotIdx = self._EQUIPMENT_START_IDX + equipmentItem.idx
                else:
                    slotIdx = self.__lastBuiltInEqIdx
                    self.__lastBuiltInEqIdx = self.__lastBuiltInEqIdx + 1
            self._addEquipmentSlot(slotIdx, intCD, item)
            self._mask |= 1 << slotIdx
            return

    def _onGunReloadTimeSet(self, currShellCD, state, skipAutoLoader):
        if self.__vehicleChangeComponent and self.__vehicleChangeComponent.isControllingVehicle:
            return
        super(PortalConsumablesPanel, self)._onGunReloadTimeSet(currShellCD, state, skipAutoLoader)

    def _onShellsAdded(self, intCD, descriptor, quantity, data, gunSettings):
        if self.__vehicleChangeComponent and self.__vehicleChangeComponent.isControllingVehicle:
            return
        super(PortalConsumablesPanel, self)._onShellsAdded(intCD, descriptor, quantity, data, gunSettings)

    def _onShellsUpdated(self, intCD, quantity, *args):
        if self.__vehicleChangeComponent and self.__vehicleChangeComponent.isControllingVehicle:
            return
        super(PortalConsumablesPanel, self)._onShellsUpdated(intCD, quantity, *args)

    def _onCurrentShellChanged(self, intCD):
        if self.__vehicleChangeComponent and self.__vehicleChangeComponent.isControllingVehicle:
            return
        super(PortalConsumablesPanel, self)._onCurrentShellChanged(intCD)

    def _onNextShellChanged(self, intCD):
        if self.__vehicleChangeComponent and self.__vehicleChangeComponent.isControllingVehicle:
            return
        super(PortalConsumablesPanel, self)._onNextShellChanged(intCD)

    def _onGunSettingsSet(self, data):
        self.__resetShellSlots()
        self.__lastBuiltInEqIdx = self._BUILTIN_EQUIPMENT_START_IDX

    def __resetShellSlots(self):
        for idx in range(self._AMMO_START_IDX, self._AMMO_END_IDX + 1):
            self._mask &= ~(1 << idx)
            self._cds[idx] = None

        return

    def _handleAbilityGlow(self, currStage, prevStage, idx, item):
        if currStage in _INACTIVE_EQUIPMENT_STAGES:
            self.as_hideGlowS(idx)
            self.as_setEquipmentActivatedS(idx, False)
        elif currStage == EQUIPMENT_STAGES.READY and (prevStage == EQUIPMENT_STAGES.COOLDOWN or prevStage == EQUIPMENT_STAGES.NOT_RUNNING):
            if self.__isPortalEquipment(item):
                self.as_setGlowS(idx, glowID=CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_SPECIAL)
            else:
                self.as_setGlowS(idx, glowID=CONSUMABLES_PANEL_SETTINGS.GLOW_ID_ORANGE_SPECIAL)
        elif currStage == EQUIPMENT_STAGES.READY and prevStage == EQUIPMENT_STAGES.READY:
            self.as_setGlowS(idx, glowID=CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN)
        elif currStage in _ACTIVE_EQUIPMENT_STAGES and prevStage not in _ACTIVE_EQUIPMENT_STAGES:
            self.as_setEquipmentActivatedS(idx, True)
        elif currStage not in _ACTIVE_EQUIPMENT_STAGES and prevStage in _ACTIVE_EQUIPMENT_STAGES:
            self.as_setEquipmentActivatedS(idx, False)

    def _updateEquipmentSlot(self, idx, item):
        super(PortalConsumablesPanel, self)._updateEquipmentSlot(idx, item)
        currStage = item.getStage()
        prevStage = item.getPrevStage()
        self._handleAbilityGlow(currStage, prevStage, idx, item)

    def __isPortalEquipment(self, item):
        return item.getDescriptor() and 'portal_ability' in item.getTags()

    def _getEquipmentIcon(self, idx, item, icon):
        if icon in self._REMAPPED_ICONS:
            icon = self._REMAPPED_ICONS.get(icon)
        return super(PortalConsumablesPanel, self)._getEquipmentIcon(idx, item, icon)

    @staticmethod
    def _buildAbilityEquipmentTooltip(ability):
        description = ability.description
        usageStr = backport.text(R.strings.portal_artefacts.ability.descr.usage(), cooldown=ability.cooldownSeconds)
        description = '\n\n'.join((description, usageStr))
        toolTip = TOOLTIP_FORMAT.format(ability.userString, description)
        return toolTip
