# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_matters/battle_matters_bonus_packer.py
import typing
import logging
from constants import PREMIUM_ENTITLEMENTS
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.battle_pass.battle_pass_bonuses_packers import ExtendedItemBonusUIPacker
from gui.impl.auxiliary.rewards_helper import BlueprintBonusTypes
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.views.lobby.battle_matters.battle_matters_vehicle_model import BattleMattersVehicleModel
from gui.impl.gen.view_models.views.lobby.battle_matters.battle_matters_main_view_model import BattleMattersMainViewModel
from gui.selectable_reward.constants import SELECTABLE_BONUS_NAME
from gui.selectable_reward.bonus_packers import SelectableBonusPacker
from gui.shared.missions.packers.bonus import VehiclesBonusUIPacker, getDefaultBonusPackersMap, BonusUIPacker, BlueprintBonusUIPacker
from gui.shared.gui_items.Vehicle import getIconResourceName
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.money import Currency
from gui.server_events.bonuses import VehiclesBonus, BlueprintsBonusSubtypes
from nations import NONE_INDEX
from helpers import dependency
from skeletons.gui.battle_matters import IBattleMattersController
from shared_utils import first
from gui.shared.missions.packers.bonus import BaseBonusUIPacker
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel
_logger = logging.getLogger(__name__)
_REWARDS_ORDER = ('vehicles',
 'battleToken',
 'tokens',
 'crewBooks',
 'customizations',
 'items',
 PREMIUM_ENTITLEMENTS.PLUS,
 PREMIUM_ENTITLEMENTS.BASIC,
 Currency.CRYSTAL,
 Currency.GOLD,
 'freeXP',
 Currency.CREDITS,
 'blueprintsAny',
 BlueprintBonusTypes.BLUEPRINTS,
 'goodies',
 'slots')
_CUSTOMIZATIONS_ORDER = ('style', 'emblem', 'camouflage', 'modification', 'decal', 'inscription', 'paint')
_DEVICES_TYPES_ORDER = (SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS,
 SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS_BIG,
 SLOT_HIGHLIGHT_TYPES.EQUIPMENT_TROPHY,
 SLOT_HIGHLIGHT_TYPES.EQUIPMENT_TROPHY_BASIC,
 SLOT_HIGHLIGHT_TYPES.EQUIPMENT_TROPHY_UPGRADED,
 SLOT_HIGHLIGHT_TYPES.EQUIPMENT_TROPHY_BIG,
 SLOT_HIGHLIGHT_TYPES.EQUIPMENT_TROPHY_BASIC_BIG,
 SLOT_HIGHLIGHT_TYPES.EQUIPMENT_TROPHY_UPGRADED_BIG,
 SLOT_HIGHLIGHT_TYPES.EQUIPMENT_MODERNIZED,
 SLOT_HIGHLIGHT_TYPES.EQUIPMENT_MODERNIZED_BIG,
 SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER,
 SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT)
_ITEMS_TYPES_ORDER = (GUI_ITEM_TYPE.OPTIONALDEVICE, GUI_ITEM_TYPE.BATTLE_BOOSTER, GUI_ITEM_TYPE.EQUIPMENT)

def _vehiclesCmp(firstModel, secondModel):
    return cmp(firstModel.getLevel(), secondModel.getLevel())


def _customizationsCmp(firstModel, secondModel):
    return indexesCmp(_CUSTOMIZATIONS_ORDER, firstModel.getIcon(), secondModel.getIcon())


def _itemsCmp(firstModel, secondModel):
    result = indexesCmp(_ITEMS_TYPES_ORDER, firstModel.getItemType(), secondModel.getItemType())
    if not result:
        result = indexesCmp(_DEVICES_TYPES_ORDER, firstModel.getOverlayType(), secondModel.getOverlayType())
    return result


_CUSTOM_SORT = {VehiclesBonus.VEHICLES_BONUS: _vehiclesCmp,
 'customizations': _customizationsCmp,
 'items': _itemsCmp}

def battleMattersSort(rewardType):
    return _CUSTOM_SORT.get(rewardType, lambda _, __: 0)


def bonusesSort(firstBonus, secondBonus):
    firstBonusName = firstBonus.getName()
    secondBonusName = secondBonus.getName()
    if firstBonusName == secondBonusName == BlueprintBonusTypes.BLUEPRINTS:
        result = blueprintsCmp(firstBonus, secondBonus)
    else:
        result = indexesCmp(_REWARDS_ORDER, firstBonusName, secondBonusName)
    return result


def indexesCmp(sequence, firstBonusName, secondBonusName):
    firstOrder = secondOrder = len(sequence)
    if firstBonusName in sequence:
        firstOrder = sequence.index(firstBonusName)
    if secondBonusName in sequence:
        secondOrder = sequence.index(secondBonusName)
    return cmp(firstOrder, secondOrder)


def blueprintsCmp(firstBonus, secondBonus):
    firstBlueprintName = firstBonus.getBlueprintName()
    secondBlueprintName = secondBonus.getBlueprintName()
    result = 0
    if firstBlueprintName == BlueprintsBonusSubtypes.UNIVERSAL_FRAGMENT:
        result = -1
    elif firstBlueprintName == secondBlueprintName == BlueprintsBonusSubtypes.NATION_FRAGMENT:
        result = _blueprintsNationCmp(firstBonus, secondBonus)
    return result


def _blueprintsNationCmp(firstBonus, secondBonus):
    return cmp(GUI_NATIONS_ORDER_INDEX.get(firstBonus.getImageCategory(), NONE_INDEX), GUI_NATIONS_ORDER_INDEX.get(secondBonus.getImageCategory(), NONE_INDEX))


def getBattleMattersBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({VehiclesBonus.VEHICLES_BONUS: BattleMattersVehiclesBonusUIPacker(),
     BlueprintBonusTypes.BLUEPRINTS: BattleMattersBlueprintBonusUIPacker(),
     SELECTABLE_BONUS_NAME: BattleMattersTokenBonusUIPacker(),
     'entitlements': BattleMattersEntitlementsBonusUIPacker(),
     'items': ExtendedItemBonusUIPacker()})
    return BonusUIPacker(mapping)


class BattleMattersBlueprintBonusUIPacker(BlueprintBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        models = super(BattleMattersBlueprintBonusUIPacker, cls)._pack(bonus)
        model = first(models)
        if model:
            fragmentName = bonus.getBlueprintName()
            if fragmentName == BlueprintsBonusSubtypes.NATION_FRAGMENT:
                lbl = cls._getNationalLbl(bonus)
            else:
                lbl = bonus.getBlueprintTooltipName()
            model.setLabel(lbl)
        return models

    @classmethod
    def _getNationalLbl(cls, bonus):
        nation = bonus.getImageCategory()
        nationName = backport.text(R.strings.blueprints.nations.dyn(nation)())
        return backport.text(R.strings.quests.bonusName.blueprints.nation(), nationName=nationName)


class BattleMattersTokenBonusUIPacker(SelectableBonusPacker):
    __battleMattersController = dependency.descriptor(IBattleMattersController)

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = IconBonusModel()
        if cls.__isVehicleReceived():
            vehicle = cls.__battleMattersController.getSelectedVehicle()
            if vehicle:
                model.setIcon(getIconResourceName(vehicle.name))
                model.setName(BattleMattersMainViewModel.NAME_VEHICLE_REWARD)
        else:
            model.setName(BattleMattersMainViewModel.NAME_TOKEN_REWARD)
            model.setValue(str(bonus.getCount()))
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        if cls.__isVehicleReceived():
            vehicle = cls.__battleMattersController.getSelectedVehicle()
            return [backport.createTooltipData(isSpecial=True, specialArgs=(vehicle.intCD,), specialAlias=TOOLTIPS_CONSTANTS.CAROUSEL_VEHICLE)]
        else:
            return [None]

    @classmethod
    def __isVehicleReceived(cls):
        quest = first(cls.__battleMattersController.getQuestsWithDelayedReward())
        return quest and quest.isCompleted() and not cls.__battleMattersController.hasDelayedRewards()

    @classmethod
    def _makeRewardItemModel(cls):
        pass

    @classmethod
    def _getTooltipSpecialAlias(cls):
        pass


class BattleMattersVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        currentVehicle = BattleMattersVehicleModel()
        rentLength = bonus.getRentDays(vehInfo)
        if rentLength:
            currentVehicle.setRentLength(rentLength)
        currentVehicle.setIsInHangar(vehicle.isInInventory)
        currentVehicle.setVehCD(vehicle.intCD)
        currentVehicle.setVehType(vehicle.type)
        currentVehicle.setLevel(vehicle.level)
        currentVehicle.setNation(vehicle.nationName)
        currentVehicle.setVehName(getNationLessName(vehicle.name))
        currentVehicle.setUserName(vehicle.userName)
        currentVehicle.setIsElite(vehicle.isElite)
        return currentVehicle


class BattleMattersEntitlementsBonusUIPacker(BaseBonusUIPacker):
    _ITEMS_TO_SKIP = {'battle_matters_rent_tiger'}

    @classmethod
    def _pack(cls, bonus):
        if bonus.getValue().id in cls._ITEMS_TO_SKIP:
            result = []
        else:
            _logger.error('Not supported entitlement %s', bonus.getValue().id)
            result = super(BattleMattersEntitlementsBonusUIPacker, cls)._pack(bonus)
        return result
