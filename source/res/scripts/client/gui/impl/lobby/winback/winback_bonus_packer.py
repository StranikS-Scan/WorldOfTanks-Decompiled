# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/winback/winback_bonus_packer.py
import logging
from collections import defaultdict, OrderedDict
from copy import deepcopy
import typing
from account_helpers.offers.offer_bonuses import NationalBlueprintOfferBonus
from blueprints.BlueprintTypes import BlueprintTypes
from blueprints.FragmentTypes import getFragmentType
from goodies.goodie_constants import GOODIE_VARIETY
from gui.impl.auxiliary.rewards_helper import BlueprintBonusTypes
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.winback.discount_vehicle_bonus_model import DiscountVehicleBonusModel
from gui.impl.gen.view_models.views.lobby.winback.rent_vehicle_bonus_model import RentVehicleBonusModel, RentType
from gui.impl.gen.view_models.views.lobby.winback.vehicle_bonus_model import VehicleBonusModel
from gui.impl.gen.view_models.views.lobby.winback.vehicle_selectable_bonus_model import VehicleSelectableBonusModel
from gui.impl.gen.view_models.views.lobby.winback.winback_blueprint_bonus_model import WinbackBlueprintBonusModel
from gui.impl.gen.view_models.views.lobby.winback.winback_reward_view_model import RewardName
from gui.impl.lobby.battle_matters.battle_matters_bonus_packer import BattleMattersBlueprintBonusUIPacker
from gui.impl.lobby.winback.winback_bonuses import WinbackVehicleBonus, WinbackVehicleDiscountBonus, WinbackSelectableBonus
from gui.impl.lobby.winback.winback_helpers import getDiscountFromGoody, getDiscountFromBlueprint
from gui.server_events.bonuses import VehiclesBonus, TokensBonus, GoodiesBonus, getNonQuestBonuses
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.missions.packers.bonus import BaseBonusUIPacker, BlueprintBonusUIPacker
from gui.shared.missions.packers.bonus import BonusUIPacker
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap
from helpers import dependency
from skeletons.gui.game_control import IWinbackController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, Optional
    from frameworks.wulf.view.array import Array
    from gui.impl.backport import TooltipData
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.server_events.bonuses import SimpleBonus
_logger = logging.getLogger(__name__)
WINBACK_DISCOUNTS = 'winbackDiscounts'
_BONUS_COUNT = 'count'

def getWinbackMapping():
    mapping = getDefaultBonusPackersMap()
    winbackBonusPacker = WinbackVehiclesBonusUIPacker()
    battleMattersBlueprintBonusPacker = BattleMattersBlueprintBonusUIPacker()
    mapping[RewardName.SELECTABLE_VEHICLE_DISCOUNT.value] = winbackBonusPacker
    mapping[RewardName.SELECTABLE_VEHICLE_FOR_GIFT.value] = winbackBonusPacker
    mapping[RewardName.VEHICLE_FOR_GIFT.value] = winbackBonusPacker
    mapping[RewardName.VEHICLE_DISCOUNT.value] = winbackBonusPacker
    mapping[RewardName.VEHICLE_FOR_RENT.value] = winbackBonusPacker
    mapping[BlueprintBonusTypes.BLUEPRINTS] = battleMattersBlueprintBonusPacker
    return mapping


def getWinbackBonusPacker():
    return BonusUIPacker(getWinbackMapping())


def getWinbackBonuses(bonuses, received=False):
    rawBonuses = deepcopy(bonuses)
    bonusesData, winbackBonusesData = cutWinbackBonuses(rawBonuses, received=received)
    simpleBonuses = []
    for bonusName, bonusValue in bonusesData.items():
        simpleBonuses.extend(getNonQuestBonuses(bonusName, bonusValue))

    winbackBonuses = handleWinbackBonusesData(winbackBonusesData) + simpleBonuses
    return winbackBonuses


def cutWinbackBonuses(bonusesData, winbackData=None, received=False):
    winbackData = winbackData or {}
    cutVehDiscountsFromBonuses(bonusesData, winbackData, received)
    cutWinbackTokens(bonusesData, winbackData)
    cutVehicles(bonusesData, winbackData)
    return (bonusesData, winbackData)


@dependency.replace_none_kwargs(goodiesCache=IGoodiesCache, itemsCache=IItemsCache)
def cutVehDiscountsFromBonuses(bonusesData, winbackData=None, received=False, goodiesCache=None, itemsCache=None):
    winbackData = {} if winbackData is None else winbackData
    winbackDiscounts = defaultdict(lambda : {BlueprintBonusTypes.BLUEPRINTS: {},
     GoodiesBonus.GOODIES: {}})
    winbackData[WINBACK_DISCOUNTS] = winbackDiscounts
    blueprints = bonusesData.get(BlueprintBonusTypes.BLUEPRINTS, {})
    goodies = bonusesData.get(GoodiesBonus.GOODIES, {})
    for goodyID in goodies.keys():
        goodyData = goodiesCache.getGoodieByID(goodyID)
        if goodyData.variety == GOODIE_VARIETY.DISCOUNT:
            winbackDiscounts[goodyData.target.targetValue][GoodiesBonus.GOODIES][goodyID] = goodies.pop(goodyID)

    if not goodies and GoodiesBonus.GOODIES in bonusesData:
        bonusesData.pop(GoodiesBonus.GOODIES)
    for fragmentID in blueprints.keys():
        if getFragmentType(fragmentID) == BlueprintTypes.VEHICLE:
            if fragmentID in winbackDiscounts.keys():
                fragmentsCount = blueprints.pop(fragmentID)
                if received:
                    vehicle = itemsCache.items.getItemByCD(fragmentID)
                    fragmentsCount, _ = itemsCache.items.blueprints.getBlueprintCount(fragmentID, vehicle.level)
                winbackDiscounts[fragmentID][BlueprintBonusTypes.BLUEPRINTS][fragmentID] = fragmentsCount

    if not blueprints and BlueprintBonusTypes.BLUEPRINTS in bonusesData:
        bonusesData.pop(BlueprintBonusTypes.BLUEPRINTS)
    return (bonusesData, winbackData)


def cutWinbackTokens(bonusesData, winbackData=None):
    if TokensBonus.TOKENS in bonusesData:
        winbackData = {} if winbackData is None else winbackData
        winbackData[TokensBonus.TOKENS] = bonusesData.pop(TokensBonus.TOKENS)
    return (bonusesData, winbackData)


def cutVehicles(bonusesData, winbackData=None):
    winbackData = {} if winbackData is None else winbackData
    vehicles = {}
    if VehiclesBonus.VEHICLES_BONUS in bonusesData:
        winbackData[VehiclesBonus.VEHICLES_BONUS] = vehicles
        vehiclesBonusesData = bonusesData[VehiclesBonus.VEHICLES_BONUS]
        if not isinstance(vehiclesBonusesData, list):
            bonusesData[VehiclesBonus.VEHICLES_BONUS] = [vehiclesBonusesData]
        slots = bonusesData.get('slots', 0)
        for vehiclesData in bonusesData[VehiclesBonus.VEHICLES_BONUS]:
            for vehCD, vehData in vehiclesData.items():
                vehicles[vehCD] = vehData
                if slots > 0 and not vehData.get('rent'):
                    vehData['slot'] = 1
                    slots -= 1

        if 'slots' in bonusesData and slots == 0:
            bonusesData.pop('slots')
        bonusesData.pop(VehiclesBonus.VEHICLES_BONUS)
    return (bonusesData, winbackData)


def _getCount(bonusData):
    return bonusData.get(_BONUS_COUNT, 0)


def handleWinbackBonusesData(bonuses):
    return handleWinbackOfferTokens(bonuses) + handleWinbackDiscounts(bonuses) + handleVehicleBonuses(bonuses)


@dependency.replace_none_kwargs(winbackController=IWinbackController)
def handleWinbackOfferTokens(bonuses, winbackController=None):
    result = []
    tokens = bonuses.get(TokensBonus.TOKENS, {})
    for tokenName, tokenData in tokens.items():
        bonusData = winbackController.parseOfferToken(tokenName.replace('_gift', ''))
        if _getCount(tokenData) > 0 and bonusData is not None:
            bonuseName = bonusData.get('name')
            if bonuseName in (RewardName.SELECTABLE_VEHICLE_DISCOUNT.value, RewardName.SELECTABLE_VEHICLE_FOR_GIFT.value):
                result.append(WinbackSelectableBonus(bonuseName, bonusData))

    return result


def handleWinbackDiscounts(bonuses):
    winbackBonuses = bonuses.get(WINBACK_DISCOUNTS)
    return [WinbackVehicleDiscountBonus(RewardName.VEHICLE_DISCOUNT.value, winbackBonuses)] if winbackBonuses else []


def handleVehicleBonuses(bonuses):
    result = []
    vehicles = bonuses.get(VehiclesBonus.VEHICLES_BONUS, {})
    if vehicles:
        rentVehicles = OrderedDict()
        vehiclesForGift = OrderedDict()
        for vehCD, vehData in vehicles.items():
            if vehData.get('rent'):
                rentVehicles[vehCD] = vehData
            vehiclesForGift[vehCD] = vehData

        if rentVehicles:
            result.append(WinbackVehicleBonus(RewardName.VEHICLE_FOR_RENT.value, rentVehicles))
        if vehiclesForGift:
            result.append(WinbackVehicleBonus(RewardName.VEHICLE_FOR_GIFT.value, vehiclesForGift))
    return result


_RENT_MAP = {RentType.TIME.value: RentType.TIME,
 RentType.BATTLES.value: RentType.BATTLES,
 RentType.WINS.value: RentType.WINS}

class WinbackVehiclesBonusUIPacker(BaseBonusUIPacker):
    _itemsCache = dependency.descriptor(IItemsCache)

    @staticmethod
    def packSelectableVehicleReward(bonus):
        model = VehicleSelectableBonusModel()
        model.setName(bonus.getName())
        model.setVehicleLvl(bonus.getLevel())
        model.setPriceDiscount(bonus.getPurchaseDiscount())
        model.setExpDiscount(bonus.getResearchDiscount())
        model.setTooltipContentId(str(R.views.lobby.winback.tooltips.SelectableRewardTooltip()))
        return [model]

    @classmethod
    def packVehicleRewards(cls, bonus):
        result = []
        vehicleCDs = bonus.getVehicleCDs()
        for vehCD in vehicleCDs:
            model = cls._createVehicleModel(vehCD, bonus)
            result.append(model)

        return result

    @classmethod
    def getToolTip(cls, bonus):
        return bonus.getTooltip()

    @classmethod
    def _createVehicleModel(cls, vehCD, bonus):
        vehicle = cls._itemsCache.items.getItemByCD(vehCD)
        rentValue = bonus.getRentValue(vehCD)
        model = cls._getVehicleModel(bool(rentValue))
        cls._packVehicleModel(vehicle, bonus, model)
        if rentValue:
            cls._packRentData(vehicle, bonus, model)
        if bonus.getName() == RewardName.VEHICLE_DISCOUNT.value:
            cls._packDiscountData(vehicle, bonus, model)
        return model

    @classmethod
    def _getVehicleModel(cls, isRent):
        return RentVehicleBonusModel() if isRent else VehicleBonusModel()

    @staticmethod
    def _packVehicleModel(vehicle, bonus, model):
        model.setName(bonus.getName())
        model.setVehicleName(getNationLessName(vehicle.name))
        model.setUserName(vehicle.shortUserName)
        model.setVehicleLvl(vehicle.level)
        model.setVehicleType(vehicle.type)
        model.setIsElite(vehicle.isElite)
        model.setNation(vehicle.nationName)

    @staticmethod
    def _packRentData(vehicle, bonus, model):
        vehCD = vehicle.intCD
        model.setRentType(bonus.getRentType(vehCD))
        model.setRentDuration(bonus.getRentValue(vehCD))

    @staticmethod
    def _packDiscountData(vehicle, bonus, model):
        vehCD = vehicle.intCD
        goodieId, blueprintsCount = bonus.getResources(vehCD)
        model.setPriceDiscount(getDiscountFromGoody(goodieId)[0])
        model.setExpDiscount(getDiscountFromBlueprint(vehCD, blueprintsCount))

    @classmethod
    def _pack(cls, bonus):
        bonusPackMethod = cls._getPackMethod(bonus.getName())
        bonusModels = []
        if bonusPackMethod:
            bonusModels.extend(bonusPackMethod(bonus))
        return bonusModels

    @classmethod
    def _getPackMethod(cls, name):
        packMethodByBonusName = {RewardName.SELECTABLE_VEHICLE_FOR_GIFT.value: cls.packSelectableVehicleReward,
         RewardName.SELECTABLE_VEHICLE_DISCOUNT.value: cls.packSelectableVehicleReward,
         RewardName.VEHICLE_DISCOUNT.value: cls.packVehicleRewards,
         RewardName.VEHICLE_FOR_GIFT.value: cls.packVehicleRewards,
         RewardName.VEHICLE_FOR_RENT.value: cls.packVehicleRewards}
        return packMethodByBonusName.get(name)


class WinbackBlueprintUIPacker(BlueprintBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(bonus.getCount()))
        model.setType(bonus.getBlueprintName())
        model.setIcon(bonus.getImageCategory())
        model.setAmountInStorage(bonus.getInventoryCount())
        return [model]

    @classmethod
    def _getBonusModel(cls):
        return WinbackBlueprintBonusModel()


class WinbackDiscountBonusUIPacker(WinbackVehiclesBonusUIPacker):

    @classmethod
    def _getVehicleModel(cls, _):
        return DiscountVehicleBonusModel()

    @staticmethod
    def _packVehicleModel(vehicle, bonus, model):
        WinbackVehiclesBonusUIPacker._packVehicleModel(vehicle, bonus, model)
        if bonus.getName() == RewardName.VEHICLE_DISCOUNT.value:
            defPrice, newPrice = bonus.getPrices(vehicle.intCD)
            defPrice = defPrice.credits
            newPrice = newPrice.credits
            xpPrice, newXPPrice = bonus.getXPs(vehicle.intCD)
        else:
            defPrice, newPrice, xpPrice, newXPPrice = (0, 0, 0, 0)
        model.setOldPrice(defPrice)
        model.setOldExp(xpPrice)
        model.setNewPrice(newPrice)
        model.setNewExp(newXPPrice)


def packWinBackBonusModelAndTooltipData(bonuses, packer, model, tooltipData=None, sort=None):
    bonusIndexTotal = 0
    bonusTooltipList = []
    if tooltipData is not None:
        bonusIndexTotal = len(tooltipData)
    for bonus in bonuses:
        if bonus.isShowInGUI():
            bonusList = packer.pack(bonus)
            if sort is not None and callable(sort):
                bonusList = sorted(bonusList, cmp=sort(bonus.getName()))
            if bonusList and tooltipData is not None:
                bonusTooltipList = packer.getToolTip(bonus)
            for bonusIndex, item in enumerate(bonusList):
                item.setIndex(bonusIndexTotal)
                bonusIdx = str(bonusIndexTotal)
                if hasattr(item, 'setTooltipId'):
                    item.setTooltipId(bonusIdx)
                model.addViewModel(item)
                if tooltipData is not None:
                    tooltipData[bonusIdx] = bonusTooltipList[bonusIndex]
                bonusIndexTotal += 1

    return
