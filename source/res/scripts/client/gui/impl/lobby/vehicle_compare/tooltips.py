# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_compare/tooltips.py
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.impl.backport import createTooltipData
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.backports.tooltips import OptDeviceTooltipBuilder, ConsumableToolitpBuilder, BattleBoostersTooltipBuilder, ShellTooltipBuilder, getSlotTooltipData
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class CmpOptDeviceTooltipBuilder(OptDeviceTooltipBuilder):

    @classmethod
    def _getTooltipSpecialAlias(cls):
        return TOOLTIPS_CONSTANTS.COMPARE_MODULE

    @classmethod
    def _getInSlotTooltipAlias(cls):
        return TOOLTIPS_CONSTANTS.COMPARE_SLOT_MODULE


class CmpConsumableToolitpBuilder(ConsumableToolitpBuilder):
    _itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def getTooltipData(cls, vehicle, slotID, intCD):
        item = cls._itemsCache.items.getItemByCD(intCD)
        return createTooltipData(tooltip=makeTooltip(item.userName, attention=VEH_COMPARE.VEHCONF_TOOLTIPS_DEVICENOTAFFECTEDTTC)) if item.name in cmp_helpers.NOT_AFFECTED_EQUIPMENTS else super(CmpConsumableToolitpBuilder, cls).getTooltipData(vehicle, slotID, intCD)

    @classmethod
    def _getTooltipSpecialAlias(cls):
        return TOOLTIPS_CONSTANTS.COMPARE_MODULE


class CmpBattleBoostersTooltipBuilder(BattleBoostersTooltipBuilder):
    itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def _getTooltipSpecialAlias(cls):
        return TOOLTIPS_CONSTANTS.BATTLE_BOOSTER_COMPARE


class CmpShellTooltipBuilder(ShellTooltipBuilder):
    itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def getPanelSlotTooltip(cls, vehicle, slotID):
        intCD = vehicle.descriptor.gun.shots[slotID].shell.compactDescr
        return cls.getTooltipData(vehicle, slotID, intCD)

    @classmethod
    def _getTooltipSpecialAlias(cls):
        return TOOLTIPS_CONSTANTS.COMPARE_SHELL


class CmpCamouflageTooltipBuilder(object):
    itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def getPanelSlotTooltip(cls, *_):
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.VEH_CMP_CUSTOMIZATION, specialArgs=[True])

    @classmethod
    def getTooltipData(cls, *_):
        return None

    @classmethod
    def getVehicle(cls, vehicle, _=None):
        return vehicle


CMP_PANEL_SLOT_TOOLTIPS = {TankSetupConstants.BATTLE_BOOSTERS: CmpBattleBoostersTooltipBuilder,
 TankSetupConstants.OPT_DEVICES: CmpOptDeviceTooltipBuilder,
 TankSetupConstants.CONSUMABLES: CmpConsumableToolitpBuilder,
 TankSetupConstants.TOGGLE_CAMOUFLAGE: CmpCamouflageTooltipBuilder,
 TankSetupConstants.TOGGLE_SHELLS: CmpShellTooltipBuilder}

def getCmpSlotTooltipData(event, vehicle, currentSlotID=None, currentSection=None):
    return getSlotTooltipData(event, vehicle, currentSlotID, currentSection, tooltipsMap=CMP_PANEL_SLOT_TOOLTIPS)
