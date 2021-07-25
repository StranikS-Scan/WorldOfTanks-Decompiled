# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/client_perk_blocks.py
from typing import TYPE_CHECKING
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from visual_script.perk_blocks import AddFactorModifierBase, RemoveFactorModifiersBase, DropAllPerkModifiersBase, PerkArgumentBase, AddEquipmentCooldownModifierBase, ModifyTerrainResistanceBase, VehicleInRangeLoopBase, RemoveEquipmentCooldownModifierBase
from gui.Scaleform.daapi.view.lobby.detachment.detachment_setup_vehicle import g_detachmentTankSetupVehicle
from constants import EQUIPMENT_COOLDOWN_MOD_SUFFIX
if TYPE_CHECKING:
    from PerksParametersController import PerksParametersController

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getPerksController(vehInvID, itemsCache=None):
    return g_detachmentTankSetupVehicle.item.getPerksController() if g_detachmentTankSetupVehicle.item and g_detachmentTankSetupVehicle.item.descriptor.type.compactDescr == vehInvID else itemsCache.items.getItemByCD(vehInvID).getPerksController()


class AddFactorModifier(AddFactorModifierBase):
    itemsCache = dependency.descriptor(IItemsCache)

    def _execute(self):
        vehIntId = self._vehId.getValue()
        perkId = self._perkId.getValue()
        scopeId = self._scopeId.getValue()
        value = self._value.getValue()
        factor = self._factor.getValue()
        getPerksController(vehIntId).modifyFactor(factor, scopeId, perkId, value)
        self._outSlot.call()


class RemoveFactorModifiers(RemoveFactorModifiersBase):
    itemsCache = dependency.descriptor(IItemsCache)

    def _execute(self):
        vehIntId = self._vehId.getValue()
        perkId = self._perkId.getValue()
        scopeId = self._scopeId.getValue()
        factor = self._factor.getValue()
        numMods = self._numMods.getValue()
        perksController = getPerksController(vehIntId)
        if numMods > 0:
            perksController.removeNumFactorModifiers(factor, scopeId, perkId, numMods)
        else:
            perksController.dropFactorModifiers(factor, scopeId, perkId)
        self._outSlot.call()


class DropAllPerkModifiers(DropAllPerkModifiersBase):
    itemsCache = dependency.descriptor(IItemsCache)

    def _execute(self):
        vehIntId = self._vehId.getValue()
        perkId = self._perkId.getValue()
        scopeId = self._scopeId.getValue()
        getPerksController(vehIntId).dropAllPerkModifiers(scopeId, perkId)
        self._outSlot.call()


class PerkArgument(PerkArgumentBase):
    pass


class AddEquipmentCooldownModifier(AddEquipmentCooldownModifierBase):
    itemsCache = dependency.descriptor(IItemsCache)

    def _execute(self):
        value = self._value.getValue()
        perk = self._perk.getValue()
        equipmentName = self._equipmentName.getValue()
        factor = equipmentName + EQUIPMENT_COOLDOWN_MOD_SUFFIX
        getPerksController(perk.vehicleID).modifyFactor(factor, perk.scopeID, perk.perkID, value)
        self._outSlot.call()


class RemoveEquipmentCooldownModifier(RemoveEquipmentCooldownModifierBase):
    itemsCache = dependency.descriptor(IItemsCache)

    def _execute(self):
        perk = self._perk.getValue()
        equipmentName = self._equipmentName.getValue()
        factor = equipmentName + EQUIPMENT_COOLDOWN_MOD_SUFFIX
        getPerksController(perk.vehicleID).dropFactorModifiers(factor, perk.scopeID, perk.perkID)
        self._outSlot.call()


class ModifyTerrainResistance(ModifyTerrainResistanceBase):
    itemsCache = dependency.descriptor(IItemsCache)

    def _execute(self):
        perk = self._perk.getValue()
        firmGroundFactor = self._firmGroundFactor.getValue()
        mediumGroundFactor = self._mediumGroundFactor.getValue()
        softGroundFactor = self._softGroundFactor.getValue()
        perksController = getPerksController(perk.vehicleID)
        perksController.modifyFactor('chassis/terrainResistance', perk.scopeID, perk.perkID, (firmGroundFactor, mediumGroundFactor, softGroundFactor))
        self._outSlot.call()


class VehicleInRangeLoop(VehicleInRangeLoopBase):

    def _execute(self):
        self._outSlot.call()
