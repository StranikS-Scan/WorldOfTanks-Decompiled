# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/backports/tooltips.py
from collections import namedtuple
import BigWorld
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl.backport import createTooltipData
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_fields import TankSetupFields
from gui.shared.gui_items.Vehicle import Vehicle
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_PanelSlotTooltip = namedtuple('_PanelSlotTooltip', 'tooltip, emptyTooltip')

class HangarModuleTooltipBuilder(object):
    itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def getPanelSlotTooltip(cls, vehicle, slotID):
        item = cls._getSlotItem(vehicle, slotID)
        return cls.getEmptyTooltip(vehicle, slotID, None) if item is None else cls.getInSlotTooltipData(vehicle, slotID, item.intCD)

    @classmethod
    def getInSlotTooltipData(cls, vehicle, slotID, intCD):
        return createTooltipData(isSpecial=True, specialAlias=cls._getInSlotTooltipAlias(), specialArgs=[intCD,
         slotID,
         -1,
         vehicle])

    @classmethod
    def getTooltipData(cls, vehicle, slotID, intCD):
        return createTooltipData(isSpecial=True, specialAlias=cls._getTooltipSpecialAlias(), specialArgs=[intCD,
         slotID,
         -1,
         vehicle])

    @classmethod
    def getEmptyTooltip(cls, *args):
        return None

    @classmethod
    def getSpecialInfoSlotTooltip(cls, *args):
        return None

    @classmethod
    def getVehicle(cls, vehicle, currentSection=None):
        return cls.itemsCache.items.getVehicleCopy(vehicle)

    @classmethod
    def _getTooltipSpecialAlias(cls):
        return TOOLTIPS_CONSTANTS.HANGAR_CARD_MODULE

    @classmethod
    def _getInSlotTooltipAlias(cls):
        return TOOLTIPS_CONSTANTS.HANGAR_MODULE

    @classmethod
    def _getSlotItem(cls, vehicle, slotID):
        raise NotImplementedError


class OptDeviceTooltipBuilder(HangarModuleTooltipBuilder):

    @classmethod
    def getEmptyTooltip(cls, vehicle, slotID, intCD):
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.OPT_DEVICE_EMPTY_SLOT, specialArgs=[TOOLTIPS.HANGAR_AMMO_PANEL_DEVICE_EMPTY, slotID, vehicle])

    @classmethod
    def getVehicle(cls, vehicle, currentSection=None):
        copyVehicle = super(OptDeviceTooltipBuilder, cls).getVehicle(vehicle, currentSection)
        copyVehicle.optDevices.dynSlotType = vehicle.optDevices.dynSlotType
        if currentSection == TankSetupConstants.OPT_DEVICES:
            copyVehicle.optDevices.setInstalled(*vehicle.optDevices.layout)
        else:
            copyVehicle.optDevices.setInstalled(*vehicle.optDevices.installed)
        return copyVehicle

    @classmethod
    def _getInSlotTooltipAlias(cls):
        return TOOLTIPS_CONSTANTS.HANGAR_SLOT_MODULE

    @classmethod
    def _getSlotItem(cls, vehicle, slotID):
        return vehicle.optDevices.installed[int(slotID)]


class ConsumableToolitpBuilder(HangarModuleTooltipBuilder):

    @classmethod
    def getEmptyTooltip(cls, *args):
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.AMMUNITION_EMPTY_SLOT, specialArgs=[TOOLTIPS.HANGAR_AMMO_PANEL_EQUIPMENT_EMPTY])

    @classmethod
    def getVehicle(cls, vehicle, currentSection=None):
        copyVehicle = super(ConsumableToolitpBuilder, cls).getVehicle(vehicle, currentSection)
        if currentSection == TankSetupConstants.CONSUMABLES:
            copyVehicle.consumables.setInstalled(*vehicle.consumables.layout)
        else:
            copyVehicle.consumables.setInstalled(*vehicle.consumables.installed)
        return copyVehicle

    @classmethod
    def _getSlotItem(cls, vehicle, slotID):
        return vehicle.consumables.installed[int(slotID)]


class HWConsumableTooltipBuilder(ConsumableToolitpBuilder):
    TOOLTIP = '#halloween.tooltips.extend:hangar/ammo_panel/hw_equipment/empty'

    @classmethod
    def getEmptyTooltip(cls, *args):
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.AMMUNITION_EMPTY_SLOT, specialArgs=[cls.TOOLTIP])

    @classmethod
    def getVehicle(cls, vehicle, currentSection=None):
        hwEqCtrl = BigWorld.player().HWAccountEquipmentController
        copyVehicle = hwEqCtrl.makeVehicleHWAdapter(super(HWConsumableTooltipBuilder, cls).getVehicle(vehicle, currentSection))
        vehicle = hwEqCtrl.makeVehicleHWAdapter(vehicle)
        if currentSection == TankSetupConstants.HWCONSUMABLES:
            copyVehicle.hwConsumables.installed = vehicle.hwConsumables.layout.copy()
        else:
            copyVehicle.hwConsumables.installed = vehicle.hwConsumables.installed.copy()
        return copyVehicle

    @classmethod
    def _getSlotItem(cls, vehicle, slotID):
        return vehicle.hwConsumables.installed[int(slotID)]


class BattleBoostersTooltipBuilder(HangarModuleTooltipBuilder):
    itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def getEmptyTooltip(cls, *_):
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.AMMUNITION_EMPTY_SLOT, specialArgs=[TOOLTIPS.HANGAR_AMMO_PANEL_BATTLEBOOSTER_EMPTY])

    @classmethod
    def getVehicle(cls, vehicle, currentSection=None):
        copyVehicle = super(BattleBoostersTooltipBuilder, cls).getVehicle(vehicle, currentSection)
        if currentSection == TankSetupConstants.BATTLE_BOOSTERS:
            copyVehicle.battleBoosters.setInstalled(*vehicle.battleBoosters.layout)
        else:
            copyVehicle.battleBoosters.setInstalled(*vehicle.battleBoosters.installed)
        return copyVehicle

    @classmethod
    def _getTooltipSpecialAlias(cls):
        return TOOLTIPS_CONSTANTS.BATTLE_BOOSTER_BLOCK

    @classmethod
    def _getInSlotTooltipAlias(cls):
        return TOOLTIPS_CONSTANTS.BATTLE_BOOSTER_BLOCK

    @classmethod
    def _getSlotItem(cls, vehicle, slotID):
        return vehicle.battleBoosters.installed[int(slotID)]


class VehModuleTooltipBuilder(HangarModuleTooltipBuilder):
    pass


class ShellTooltipBuilder(HangarModuleTooltipBuilder):
    itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def _getSlotItem(cls, vehicle, slotID):
        return vehicle.shells.installed[int(slotID)]

    @classmethod
    def _getInSlotTooltipAlias(cls):
        return TOOLTIPS_CONSTANTS.TECH_MAIN_SHELL

    @classmethod
    def _getTooltipSpecialAlias(cls):
        return TOOLTIPS_CONSTANTS.TECH_MAIN_SHELL

    @classmethod
    def getVehicle(cls, vehicle, currentSection=None):
        copyVehicle = super(ShellTooltipBuilder, cls).getVehicle(vehicle, currentSection)
        if currentSection == TankSetupConstants.SHELLS:
            copyVehicle.shells.setInstalled(*vehicle.shells.layout)
        else:
            copyVehicle.shells.setInstalled(*vehicle.shells.installed)
        return copyVehicle


class BattleAbilitiesToolitpBuilder(HangarModuleTooltipBuilder):
    itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def getInSlotTooltipData(cls, vehicle, slotID, intCD):
        return cls.getTooltipData(vehicle, slotID, intCD)

    @classmethod
    def getTooltipData(cls, _, slotID, intCD):
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.EPIC_SKILL_SLOT_INFO, specialArgs=[intCD, slotID])

    @classmethod
    def getEmptyTooltip(cls, *_):
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.AMMUNITION_EMPTY_SLOT, specialArgs=[TOOLTIPS.HANGAR_AMMO_PANEL_BATTLEABILITY_EMPTY])

    @classmethod
    def getSpecialInfoSlotTooltip(cls, vehicle, slotID, intCD):
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.EPIC_SKILL_SLOT_SETUP_INFO, specialArgs=[])

    @classmethod
    def getVehicle(cls, vehicle, currentSection=None):
        copyVehicle = super(BattleAbilitiesToolitpBuilder, cls).getVehicle(vehicle, currentSection)
        if currentSection == TankSetupConstants.BATTLE_ABILITIES:
            copyVehicle.battleAbilities.setInstalled(*vehicle.battleAbilities.layout)
        else:
            copyVehicle.battleAbilities.setInstalled(*vehicle.battleAbilities.installed)
        return copyVehicle

    @classmethod
    def _getSlotItem(cls, vehicle, slotID):
        return vehicle.battleAbilities.installed[int(slotID)]


PANEL_SLOT_TOOLTIPS = {TankSetupConstants.BATTLE_BOOSTERS: BattleBoostersTooltipBuilder,
 TankSetupConstants.BATTLE_ABILITIES: BattleAbilitiesToolitpBuilder,
 TankSetupConstants.OPT_DEVICES: OptDeviceTooltipBuilder,
 TankSetupConstants.CONSUMABLES: ConsumableToolitpBuilder,
 TankSetupConstants.HWCONSUMABLES: HWConsumableTooltipBuilder,
 TankSetupConstants.SHELLS: ShellTooltipBuilder}

def getSlotTooltipData(event, vehicle, currentSlotID, currentSection=None, tooltipsMap=None):
    tooltipsMap = tooltipsMap or PANEL_SLOT_TOOLTIPS
    intCD = event.getArgument('intCD')
    slotID = event.getArgument('slotId')
    slotType = event.getArgument('slotType')
    tooltipId = event.getArgument('tooltipId')
    tooltipBuilder = tooltipsMap.get(slotType)
    if tooltipBuilder is None:
        return
    else:
        copyVehicle = tooltipBuilder.getVehicle(vehicle, currentSection)
        if event.getArgument('fieldType') == TankSetupFields.TANK_SETUP_CARD:
            if slotType != currentSection:
                return
            return tooltipBuilder.getTooltipData(copyVehicle, currentSlotID, int(intCD))
        return tooltipBuilder.getSpecialInfoSlotTooltip(copyVehicle, currentSlotID, copyVehicle.intCD) if tooltipId == TankSetupConstants.SPECIAL_SETUP_INFO_SLOT_TOOLTIP else tooltipBuilder.getPanelSlotTooltip(copyVehicle, int(slotID))


def getSlotSpecTooltipData(event, tooltipId):
    isClickable = event.getArgument('isClickable')
    isDyn = event.getArgument('isDyn')
    spec = event.getArgument('spec')
    return createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=[spec, isDyn, isClickable])


def getShellsPriceDiscountTooltipData(event, tooltipId):
    return createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(event.getArgument('price'), event.getArgument('defPrice'), event.getArgument('currencyType')))
