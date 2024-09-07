# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/lobby/views/winback_bonus_packer.py
import logging
from collections import defaultdict, OrderedDict
from copy import deepcopy
import typing
from helpers import dependency
from constants import VERSUS_AI_PROGRESSION_TOKEN_PREFIX
from account_helpers.offers.offer_bonuses import NationalBlueprintOfferBonus
from blueprints.BlueprintTypes import BlueprintTypes
from blueprints.FragmentTypes import getFragmentType
from goodies.goodie_constants import GOODIE_VARIETY
from gui.battle_pass.battle_pass_bonuses_packers import getBattlePassBonusPacker
from gui.battle_pass.battle_pass_bonuses_packers import TmanTemplateBonusPacker
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import BlueprintBonusTypes
from gui.impl.backport import createTooltipData, TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel
from gui.server_events.bonuses import getNonQuestBonuses, VehiclesBonus, GoodiesBonus
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.missions.packers.bonus import BonusUIPacker, BaseBonusUIPacker, BlueprintBonusUIPacker, SimpleBonusUIPacker, TokenBonusUIPacker, getLocalizedBonusName, BACKPORT_TOOLTIP_CONTENT_ID
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from gui.server_events.bonuses import CurrenciesBonus
from skeletons.gui.game_control import IWinbackController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache
from winback.gui.impl.gen.view_models.views.lobby.views.discount_vehicle_bonus_model import DiscountVehicleBonusModel
from winback.gui.impl.gen.view_models.views.lobby.views.rent_vehicle_bonus_model import RentVehicleBonusModel, RentType
from winback.gui.impl.gen.view_models.views.lobby.views.vehicle_bonus_model import VehicleBonusModel
from winback.gui.impl.gen.view_models.views.lobby.views.vehicle_selectable_bonus_model import VehicleSelectableBonusModel
from winback.gui.impl.gen.view_models.views.lobby.views.winback_blueprint_bonus_model import WinbackBlueprintBonusModel
from winback.gui.impl.gen.view_models.views.lobby.views.winback_reward_view_model import RewardName
from winback.gui.impl.lobby.views.winback_bonuses import WinbackVehicleBonus, WinbackVehicleDiscountBonus, WinbackSelectableBonus
from winback.gui.impl.lobby.winback_helpers import getDiscountFromGoody, getDiscountFromBlueprint
from winback.gui.selectable_reward.selectable_reward_manager import WinbackSelectableRewardManager
if typing.TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, Optional
    from frameworks.wulf.view.array import Array
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.server_events.bonuses import SimpleBonus, TmanTemplateTokensBonus
_logger = logging.getLogger(__name__)
WINBACK_DISCOUNTS = 'winbackDiscounts'
_BONUS_COUNT = 'count'

def getWinbackBonusPacker():
    packer = getBattlePassBonusPacker()
    extendedCurrencyBonusUIPacker = ExtendedCurrencyBonusUIPacker()
    tokenBonusPacker = WinbackTokenBonusUIPacker()
    winbackSelectableBonusPacker = WinbackSelectableVehiclesBonusUIPacker()
    winbackBonusPacker = WinbackVehiclesBonusUIPacker()
    packer.getPackers().update({'currencies': CurrenciesBonusUIPacker(),
     Currency.CREDITS: extendedCurrencyBonusUIPacker,
     Currency.CRYSTAL: extendedCurrencyBonusUIPacker,
     'tokens': tokenBonusPacker,
     'battleToken': tokenBonusPacker,
     'tmanToken': TmanTemplateCountableBonusPacker(),
     RewardName.SELECTABLE_VEHICLE_DISCOUNT.value: winbackSelectableBonusPacker,
     RewardName.SELECTABLE_VEHICLE_FOR_GIFT.value: winbackSelectableBonusPacker,
     RewardName.VEHICLE_FOR_GIFT.value: winbackBonusPacker,
     RewardName.VEHICLE_DISCOUNT.value: winbackBonusPacker,
     RewardName.VEHICLE_FOR_RENT.value: winbackBonusPacker})
    return packer


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


@dependency.replace_none_kwargs(winbackController=IWinbackController)
def cutWinbackTokens(bonusesData, winbackData=None, winbackController=None):
    if WinbackSelectableBonus.TOKENS in bonusesData:
        winbackData[WinbackSelectableBonus.TOKENS] = {token:bonusesData[WinbackSelectableBonus.TOKENS].pop(token) for token in bonusesData[WinbackSelectableBonus.TOKENS].keys() if winbackController.isWinbackOfferToken(token)}
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


def isSelectableBonus(bonusName):
    return bonusName in (RewardName.SELECTABLE_VEHICLE_DISCOUNT.value, RewardName.SELECTABLE_VEHICLE_FOR_GIFT.value)


def handleWinbackBonusesData(bonuses):
    return handleWinbackOfferTokens(bonuses) + handleWinbackDiscounts(bonuses) + handleVehicleBonuses(bonuses)


def handleWinbackOfferTokens(bonuses):
    result = []
    tokens = (tID for tID, tData in bonuses.get(WinbackSelectableBonus.TOKENS, {}).items() if _getCount(tData) > 0 and isSelectableBonus(WinbackSelectableRewardManager.getSelectableBonusName(tID)))
    for tokenID in tokens:
        result.append(WinbackSelectableRewardManager.createBonusFromId(tokenID.replace('_gift', '')))

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

def packWinbackBonusModelAndTooltipData(bonuses, packer, model, tooltipData=None, sort=None):
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
                bonusContentIdList = packer.getContentId(bonus)
            for bonusIndex, item in enumerate(bonusList):
                item.setIndex(bonusIndexTotal)
                bonusIdx = str(bonusIndexTotal)
                if hasattr(item, 'setTooltipId'):
                    item.setTooltipId(bonusIdx)
                if tooltipData is not None:
                    tooltipData[bonusIdx] = bonusTooltipList[bonusIndex]
                    item.setTooltipContentId(str(bonusContentIdList[bonusIndex]))
                bonusIndexTotal += 1
                model.addViewModel(item)

    return


class WinbackSelectableVehiclesBonusUIPacker(BaseBonusUIPacker):
    _eventsCache = dependency.descriptor(IEventsCache)

    @classmethod
    def getToolTip(cls, bonus):
        return bonus.getTooltip()

    @classmethod
    def _pack(cls, bonus):
        model = VehicleSelectableBonusModel()
        model.setName(bonus.getName())
        model.setVehicleLvl(bonus.getLevel())
        model.setPriceDiscount(bonus.getPurchaseDiscount())
        model.setExpDiscount(bonus.getResearchDiscount())
        return [model]

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.winback.lobby.tooltips.SelectableRewardTooltip()]


class WinbackVehiclesBonusUIPacker(BaseBonusUIPacker):
    _itemsCache = dependency.descriptor(IItemsCache)

    @staticmethod
    def _getToolTip(bonus):
        return bonus.getTooltip()

    @staticmethod
    def _getContentId(bonus):
        return [BACKPORT_TOOLTIP_CONTENT_ID] * len(bonus.getValue().keys())

    @classmethod
    def _pack(cls, bonus):
        result = []
        vehicleCDs = bonus.getVehicleCDs()
        for vehCD in vehicleCDs:
            model = cls._createVehicleModel(vehCD, bonus)
            result.append(model)

        return result

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


class TmanTemplateCountableBonusPacker(TmanTemplateBonusPacker):

    @classmethod
    def _packTmanTemplateToken(cls, tokenID, bonus):
        model = super(TmanTemplateCountableBonusPacker, cls)._packTmanTemplateToken(tokenID, bonus)
        tokenRecord = bonus.getTokens()[tokenID]
        if tokenRecord.count > 1:
            model.setValue(str(tokenRecord.count))
        return model


class ExtendedCurrencyBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setUserName(label)
        model.setValue(str(bonus.getValue()))
        model.setIcon(bonus.getName())
        model.setBigIcon(bonus.getName())
        return model

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.winback.lobby.tooltips.CompensationTooltip()] if bonus.isCompensation() else super(ExtendedCurrencyBonusUIPacker, cls)._getContentId(bonus)

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()

    @classmethod
    def _getToolTip(cls, bonus):
        if bonus.isCompensation():
            ctx = bonus.getContext()
            specialArgs = {'isDiscount': ctx.get('isDiscount', False),
             'level': ctx.get('level', -1),
             'bonuses': (bonus,)}
            return [createTooltipData(isSpecial=True, specialArgs=specialArgs)]
        return super(ExtendedCurrencyBonusUIPacker, cls)._getToolTip(bonus)


class CurrenciesBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        label = getLocalizedBonusName(bonus.getCode())
        return [cls._packSingleBonus(bonus, label if label else '')]

    @classmethod
    def _packCommon(cls, bonus, model):
        model.setName(bonus.getCode())
        model.setIsCompensation(bonus.isCompensation())
        return model

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(bonus.getValue()))
        model.setLabel(label)
        model.setUserName(label)
        model.setBigIcon(bonus.getName())
        return model

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()


VERSUS_AI_PROGRESSION_TOKEN_TYPE = 'VersusAIProgressionToken'

class WinbackTokenBonusUIPacker(TokenBonusUIPacker):

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        if tokenID.startswith(VERSUS_AI_PROGRESSION_TOKEN_PREFIX):
            return VERSUS_AI_PROGRESSION_TOKEN_TYPE
        super(WinbackTokenBonusUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

    @classmethod
    def _getTooltipsPackers(cls):
        packers = super(WinbackTokenBonusUIPacker, cls)._getTooltipsPackers()
        packers.update({VERSUS_AI_PROGRESSION_TOKEN_TYPE: cls.__getWinbackProgressionTooltip})
        return packers

    @classmethod
    def __getWinbackProgressionTooltip(cls, _, token):
        tokenBase = R.strings.winback.quests.bonuses.progressionToken.dyn(cls.__getProgressionNameFromToken(token))
        return createTooltipData(makeTooltip(backport.text(tokenBase.header()), backport.text(tokenBase.body())))

    @classmethod
    def _getTokenBonusPackers(cls):
        packers = super(WinbackTokenBonusUIPacker, cls)._getTokenBonusPackers()
        packers.update({VERSUS_AI_PROGRESSION_TOKEN_TYPE: cls.__packWinbackProgressionToken})
        return packers

    @classmethod
    def __packWinbackProgressionToken(cls, model, bonus, complexToken, token):
        model.setValue(str(bonus.getCount()))
        name = 'token_{}'.format(cls.__getProgressionNameFromToken(token))
        image = R.images.winback.gui.maps.icons.progression.dyn(name)
        model.setIconSmall(backport.image(image()))
        model.setIconBig(backport.image(image()))
        return model

    @classmethod
    def __getProgressionNameFromToken(cls, token):
        name = token.id.split(':')[1].split('_')[-1]
        return name
