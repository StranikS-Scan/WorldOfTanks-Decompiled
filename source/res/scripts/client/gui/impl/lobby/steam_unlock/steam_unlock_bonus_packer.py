# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/steam_unlock/steam_unlock_bonus_packer.py
from copy import deepcopy
import typing
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.gen.view_models.views.lobby.common.reward_item_model import RewardItemModel
from gui.server_events.bonuses import getNonQuestBonuses, VehiclesBonus
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.missions.packers.bonus import BonusUIPacker, getDefaultBonusPackersMap, CustomizationBonusUIPacker, VehiclesBonusUIPacker
if typing.TYPE_CHECKING:
    from gui.impl.backport import TooltipData
    from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
    from gui.server_events.bonuses import CustomizationsBonus, SimpleBonus
    from gui.shared.gui_items.Vehicle import Vehicle
    from typing import Any, Dict, List
CUSTOMIZATIONS_BONUS_NAME = 'customizations'
BONUSES_ORDER = [VehiclesBonus.VEHICLES_BONUS, CUSTOMIZATIONS_BONUS_NAME]

def getSteamUnlockBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({CUSTOMIZATIONS_BONUS_NAME: SteamUnlockCustomizationBonusUIPacker(),
     VehiclesBonus.VEHICLES_BONUS: SteamUnlockVehiclesBonusUIPacker()})
    return BonusUIPacker(mapping)


def getSteamUnlockBonuses(bonuses):
    rawBonuses = deepcopy(bonuses)
    cutVehicles(rawBonuses)
    simpleBonuses = []
    for bonusName, bonusValue in rawBonuses.items():
        simpleBonuses.extend(getNonQuestBonuses(bonusName, bonusValue))

    simpleBonuses.sort(key=sortBonusesByKey)
    return simpleBonuses


def cutVehicles(bonusesData):
    if VehiclesBonus.VEHICLES_BONUS in bonusesData:
        vehiclesBonusesData = bonusesData[VehiclesBonus.VEHICLES_BONUS]
        if not isinstance(vehiclesBonusesData, list):
            bonusesData[VehiclesBonus.VEHICLES_BONUS] = [vehiclesBonusesData]
        slots = bonusesData.get('slots', 0)
        for vehiclesData in bonusesData[VehiclesBonus.VEHICLES_BONUS]:
            for vehData in vehiclesData.values():
                if slots > 0 and not vehData.get('rent'):
                    vehData['slot'] = 1
                    slots -= 1

        if 'slots' in bonusesData and slots == 0:
            bonusesData.pop('slots')


def sortBonusesByKey(bonus):
    bonusName = bonus.getName()
    return BONUSES_ORDER.index(bonusName) if bonusName in BONUSES_ORDER else len(BONUSES_ORDER) + 1


class SteamUnlockVehiclesBonusUIPacker(VehiclesBonusUIPacker):
    _SPECIAL_ALIAS = TOOLTIPS_CONSTANTS.EXTENDED_AWARD_VEHICLE

    @classmethod
    def _packTooltip(cls, bonus, vehicle, vehInfo):
        tooltipData = super(SteamUnlockVehiclesBonusUIPacker, cls)._packTooltip(bonus, vehicle, vehInfo)
        tooltipData.specialArgs.extend([bonus.getTmanRoleLevel(vehInfo) > 0, vehInfo.get('slot', 0) > 0, False])
        return tooltipData


class SteamUnlockCustomizationBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(SteamUnlockCustomizationBonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        customizationItem = bonus.getC11nItem(item)
        model.setIcon('_'.join([customizationItem.itemTypeName, str(customizationItem.intCD)]))
        model.setLabel(customizationItem.userName)
        if customizationItem.itemTypeID == GUI_ITEM_TYPE.STYLE:
            model.setValue('')
        return model

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()
