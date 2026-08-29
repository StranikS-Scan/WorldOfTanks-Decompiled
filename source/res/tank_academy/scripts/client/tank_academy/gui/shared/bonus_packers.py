# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/shared/bonus_packers.py
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
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.selectable_reward.constants import SELECTABLE_BONUS_NAME
from gui.selectable_reward.bonus_packers import SelectableBonusPacker
from gui.shared.missions.packers.bonus import VehiclesBonusUIPacker, getDefaultBonusPackersMap, BonusUIPacker, BlueprintBonusUIPacker, SimpleBonusUIPacker, TokenBonusUIPacker, CrewBookBonusUIPacker, PremiumDaysBonusPacker, CustomizationBonusUIPacker
from gui.techtree.techtree_dp import g_techTreeDP
from gui.shared.gui_items.Vehicle import getNationLessName, getIconResourceName
from gui.shared.money import Currency
from gui.server_events.awards_formatters import BATTLE_BONUS_X5_TOKEN
from gui.server_events.bonuses import VehiclesBonus, BlueprintsBonusSubtypes, X5BattleTokensBonus, getNonQuestBonuses
from items.components.crew_books_constants import CREW_BOOK_RARITY
from nations import NONE_INDEX
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import ITankAcademyController
from shared_utils import first
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.tank_academy_bonus_model import TankAcademyBonusModel
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.tank_academy_vehicle_model import TankAcademyVehicleModel
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel
_logger = logging.getLogger(__name__)
_REWARDS_ORDER = (SELECTABLE_BONUS_NAME,
 VehiclesBonus.VEHICLES_BONUS,
 Currency.CRYSTAL,
 Currency.GOLD,
 PREMIUM_ENTITLEMENTS.PLUS,
 PREMIUM_ENTITLEMENTS.BASIC,
 'goodies',
 'crewBooks',
 'freeXP',
 Currency.CREDITS,
 'items',
 'customizations',
 'slots',
 'berths',
 'blueprintsAny',
 BlueprintBonusTypes.BLUEPRINTS,
 'tokens')
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
    return cmp(secondModel.getLevel(), firstModel.getLevel())


def _customizationsCmp(firstModel, secondModel):
    return _indexesCmp(_CUSTOMIZATIONS_ORDER, firstModel.getIcon(), secondModel.getIcon())


def _itemsCmp(firstModel, secondModel):
    result = _indexesCmp(_ITEMS_TYPES_ORDER, firstModel.getItemType(), secondModel.getItemType())
    if not result:
        result = _indexesCmp(_DEVICES_TYPES_ORDER, firstModel.getOverlayType(), secondModel.getOverlayType())
    return result


_CUSTOM_SORT = {VehiclesBonus.VEHICLES_BONUS: _vehiclesCmp,
 'customizations': _customizationsCmp,
 'items': _itemsCmp}

def _tankAcademySort(rewardType):
    return _CUSTOM_SORT.get(rewardType, lambda _, __: 0)


def _bonusesSort(firstBonus, secondBonus):
    firstBonusName = firstBonus.getName()
    secondBonusName = secondBonus.getName()
    if firstBonusName == secondBonusName == BlueprintBonusTypes.BLUEPRINTS:
        result = _blueprintsCmp(firstBonus, secondBonus)
    else:
        result = _indexesCmp(_REWARDS_ORDER, firstBonusName, secondBonusName)
    return result


def _indexesCmp(sequence, firstBonusName, secondBonusName):
    firstOrder = secondOrder = len(sequence)
    if firstBonusName in sequence:
        firstOrder = sequence.index(firstBonusName)
    if secondBonusName in sequence:
        secondOrder = sequence.index(secondBonusName)
    return cmp(firstOrder, secondOrder)


def _blueprintsCmp(firstBonus, secondBonus):
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


def _isEssentialCmp(firstBonus, secondBonus):
    firstIsEssential = _isEssentialBonus(firstBonus)
    secondIsEssential = _isEssentialBonus(secondBonus)
    return cmp(secondIsEssential, firstIsEssential)


def _isEssentialBonus(bonus):
    return bonus.getIsEssential() if isinstance(bonus, TankAcademyBonusModel) else False


def _isVehicleBonusModel(bonusModel):
    return isinstance(bonusModel, TankAcademyVehicleModel)


def _isTokenVehicleBonusModel(bonusModel):
    return False if not isinstance(bonusModel, TankAcademyBonusModel) else bonusModel.getName() == TankAcademyBonusModel.NAME_TOKEN_VEHICLE_REWARD


_ESSENTIAL_REWARDS = (Currency.GOLD,
 Currency.CREDITS,
 PREMIUM_ENTITLEMENTS.PLUS,
 PREMIUM_ENTITLEMENTS.BASIC,
 'freeXP',
 SELECTABLE_BONUS_NAME,
 VehiclesBonus.VEHICLES_BONUS)
_ESSENTIAL_TOKENS_REWARDS = (BATTLE_BONUS_X5_TOKEN,)
_ESSENTIAL_CREW_BOOKS_REWARDS = (CREW_BOOK_RARITY.UNIVERSAL, CREW_BOOK_RARITY.UNIVERSAL_GUIDE)

def getTankAcademyBonusPacker():
    mapping = getDefaultBonusPackersMap()
    simpleBonusUIPacker = TankAcademySimpleBonusUIPacker()
    premiumDaysBonusUIPacker = TankAcademyPremiumDaysBonusUIPacker()
    mapping.update({Currency.GOLD: simpleBonusUIPacker,
     Currency.CREDITS: simpleBonusUIPacker,
     PREMIUM_ENTITLEMENTS.BASIC: premiumDaysBonusUIPacker,
     PREMIUM_ENTITLEMENTS.PLUS: premiumDaysBonusUIPacker,
     'freeXP': simpleBonusUIPacker,
     'tokens': TankAcademyTokenBonusUIPacker(),
     'crewBooks': TankAcademyCrewBookBonusUIPacker(),
     VehiclesBonus.VEHICLES_BONUS: TankAcademyVehiclesBonusUIPacker(),
     BlueprintBonusTypes.BLUEPRINTS: TankAcademyBlueprintBonusUIPacker(),
     SELECTABLE_BONUS_NAME: TankAcademySelectableBonusUIPacker(),
     'items': ExtendedItemBonusUIPacker(),
     'customizations': TankAcademyCustomizationBonusUIPacker()})
    return BonusUIPacker(mapping)


class TankAcademyBlueprintBonusUIPacker(BlueprintBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        models = super(TankAcademyBlueprintBonusUIPacker, cls)._pack(bonus)
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


class TankAcademyCustomizationBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for item in bonus.getCustomizations():
            if item is None:
                continue
            c11nItem = bonus.getC11nItem(item)
            result.append(cls._packSingleBonus(bonus, item, cls._getLabel(c11nItem)))

        return result

    @classmethod
    def _getLabel(cls, c11nItem):
        return c11nItem.userName


class TankAcademySimpleBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = super(TankAcademySimpleBonusUIPacker, cls)._packSingleBonus(bonus, label)
        model.setIsEssential(bonus.getName() in _ESSENTIAL_REWARDS)
        return model

    @classmethod
    def _getBonusModel(cls):
        return TankAcademyBonusModel()


class TankAcademyPremiumDaysBonusUIPacker(PremiumDaysBonusPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = super(TankAcademyPremiumDaysBonusUIPacker, cls)._packSingleBonus(bonus, label)
        model.setIsEssential(bonus.getName() in _ESSENTIAL_REWARDS)
        return model

    @classmethod
    def _getBonusModel(cls):
        return TankAcademyBonusModel()


class TankAcademyTokenBonusUIPacker(TokenBonusUIPacker):

    @classmethod
    def _packToken(cls, bonusPacker, bonus, *args):
        if isinstance(bonus, X5BattleTokensBonus):
            model = TankAcademyBonusModel()
        else:
            model = TokenBonusModel()
        cls._packCommon(bonus, model)
        return bonusPacker(model, bonus, *args)

    @classmethod
    def _getTokenBonusPackers(cls):
        tokenBonusPackers = super(TankAcademyTokenBonusUIPacker, cls)._getTokenBonusPackers()
        tokenBonusPackers.update({BATTLE_BONUS_X5_TOKEN: cls.__packBattleBonusX5Token})
        return tokenBonusPackers

    @classmethod
    def __packBattleBonusX5Token(cls, model, bonus, *args):
        model.setName(BATTLE_BONUS_X5_TOKEN)
        model.setValue(str(bonus.getCount()))
        model.setLabel(bonus.getUserName())
        model.setIcon(BATTLE_BONUS_X5_TOKEN)
        model.setIsEssential(BATTLE_BONUS_X5_TOKEN in _ESSENTIAL_TOKENS_REWARDS)
        return model


class TankAcademyCrewBookBonusUIPacker(CrewBookBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, book, count):
        model = super(TankAcademyCrewBookBonusUIPacker, cls)._packSingleBonus(bonus, book, count)
        model.setIsEssential(book.getBookType() in _ESSENTIAL_CREW_BOOKS_REWARDS)
        return model

    @classmethod
    def _getBonusModel(cls):
        return TankAcademyBonusModel()


class TankAcademySelectableBonusUIPacker(SelectableBonusPacker):
    __tankAcademyController = dependency.descriptor(ITankAcademyController)

    @classmethod
    def _packSingleBonus(cls, bonus):
        tokenID = first(bonus.getValue().iterkeys())
        model = TankAcademyBonusModel()
        model.setIsEssential(bonus.getName() in _ESSENTIAL_REWARDS)
        if cls.__tankAcademyController.isOfferRewardObtained(tokenID):
            vehicle = cls.__tankAcademyController.getSelectedVehicle(tokenID)
            if vehicle:
                model.setIcon(getNationLessName(vehicle.name))
                model.setName(TankAcademyBonusModel.NAME_VEHICLE_REWARD)
                model.setTier(vehicle.level)
                model.setIsPremium(vehicle.isPremium or vehicle.isElite)
                model.setType(vehicle.type)
                model.setLabel(vehicle.descriptor.type.shortUserString)
        else:
            model.setName(TankAcademyBonusModel.NAME_TOKEN_VEHICLE_REWARD)
            model.setValue(tokenID)
            properties = cls.__tankAcademyController.getOfferProperties(tokenID)
            if properties:
                model.setTier(properties.get('giftVehiclesLevel'))
                model.setIsPremium('giftPremiumVehicles' in properties)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        offerToken = first(bonus.getValue().iterkeys())
        if cls.__tankAcademyController.isOfferRewardObtained(offerToken):
            vehicle = cls.__tankAcademyController.getSelectedVehicle(offerToken)
            return [backport.createTooltipData(isSpecial=True, specialArgs=(vehicle.intCD,), specialAlias=TOOLTIPS_CONSTANTS.CAROUSEL_VEHICLE)]
        else:
            return [None]

    @classmethod
    def _makeRewardItemModel(cls):
        pass

    @classmethod
    def _getTooltipSpecialAlias(cls):
        pass


class TankAcademyVehiclesBonusUIPacker(VehiclesBonusUIPacker):
    __itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        currentVehicle = TankAcademyVehicleModel()
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
        currentVehicle.setIsPremium(vehicle.isPremium)
        currentVehicle.setRoleKey(vehicle.roleLabel or '')
        currentVehicle.setIsBranchContinuation(cls.__isBranchContinuation(vehicle))
        return currentVehicle

    @classmethod
    def __isBranchContinuation(cls, vehicle):
        g_techTreeDP.load()
        parentCDs = g_techTreeDP.getTopLevel(vehicle.intCD)
        if not parentCDs:
            return False
        unlocked = cls.__itemsCache.items.stats.unlocks
        return any((parentCD in unlocked for parentCD in parentCDs))


def _getPackedBonusesAndTooltipList(bonuses):
    packedBonusAndTooltipList = []
    packer = getTankAcademyBonusPacker()
    bonuses = sorted(bonuses, cmp=_bonusesSort)
    for bonus in bonuses:
        if bonus.isShowInGUI():
            bonusList = packer.pack(bonus)
            bonusTooltipList = packer.getToolTip(bonus)
            merged = zip(bonusList, bonusTooltipList)
            merged.sort(cmp=_tankAcademySort(bonus.getName()), key=lambda x: x[0])
            packedBonusAndTooltipList.extend(merged)

    packedBonusAndTooltipList.sort(cmp=_isEssentialCmp, key=lambda x: x[0])
    return packedBonusAndTooltipList


def _setBonusModelIndexAndTooltipId(bonusModel, index):
    tooltipId = str(index)
    if hasattr(bonusModel, 'setIndex'):
        bonusModel.setIndex(index)
    if hasattr(bonusModel, 'setTooltipId'):
        bonusModel.setTooltipId(tooltipId)
    return tooltipId


def _makeBonusModelFromVehicle(vehicleModel):
    bonusModel = TankAcademyBonusModel()
    bonusModel.setName(TankAcademyBonusModel.NAME_VEHICLE_REWARD)
    bonusModel.setIcon(getIconResourceName(vehicleModel.getVehName()))
    bonusModel.setLabel(vehicleModel.getUserName())
    bonusModel.setTier(vehicleModel.getLevel())
    bonusModel.setIsPremium(vehicleModel.getIsPremium())
    bonusModel.setType(vehicleModel.getVehType())
    return bonusModel


def _getRewardBonusModel(bonusModel):
    return _makeBonusModelFromVehicle(bonusModel) if isinstance(bonusModel, TankAcademyVehicleModel) else bonusModel


def _packBonusModelAndTooltipData(packedBonusAndTooltipList, model, tooltipData):
    bonusIndexTotal = len(tooltipData) if tooltipData else 0
    for bonusModel, tooltip in packedBonusAndTooltipList:
        rewardBonusModel = _getRewardBonusModel(bonusModel)
        tooltipId = _setBonusModelIndexAndTooltipId(rewardBonusModel, bonusIndexTotal)
        model.addViewModel(rewardBonusModel)
        if tooltipData is not None:
            tooltipData[tooltipId] = tooltip
        bonusIndexTotal += 1

    return


def packBonusModelAndTooltipData(bonuses, model, tooltipData):
    packedBonusAndTooltipList = _getPackedBonusesAndTooltipList(bonuses)
    _packBonusModelAndTooltipData(packedBonusAndTooltipList, model, tooltipData)


def _getBonuses(rewards):
    bonuses = []
    for key, value in rewards.iteritems():
        bonus = getNonQuestBonuses(key, value)
        if bonus:
            bonuses.extend(bonus)

    return bonuses


_MAX_LEN_MAIN_REWARDS = 3

def packRewardsModelAndTooltipData(rewards, mainRewards, otherRewards, tooltipData):
    bonuses = _getBonuses(rewards)
    packedBonusAndTooltipList = _getPackedBonusesAndTooltipList(bonuses)
    mainPackedBonusAndTooltipList = []
    otherPackedBonusAndTooltipList = []
    for bonusModel, tooltip in packedBonusAndTooltipList:
        if _isVehicleBonusModel(bonusModel) or _isTokenVehicleBonusModel(bonusModel):
            mainPackedBonusAndTooltipList.append((bonusModel, tooltip))
        otherPackedBonusAndTooltipList.append((bonusModel, tooltip))

    if not mainPackedBonusAndTooltipList:
        otherPackedBonusAndTooltipList = []
        for bonusModel, tooltip in packedBonusAndTooltipList:
            if _isEssentialBonus(bonusModel) and len(mainPackedBonusAndTooltipList) < _MAX_LEN_MAIN_REWARDS:
                mainPackedBonusAndTooltipList.append((bonusModel, tooltip))
            otherPackedBonusAndTooltipList.append((bonusModel, tooltip))

        if len(mainPackedBonusAndTooltipList) == _MAX_LEN_MAIN_REWARDS:
            mainPackedBonusAndTooltipList[0], mainPackedBonusAndTooltipList[1] = mainPackedBonusAndTooltipList[1], mainPackedBonusAndTooltipList[0]
    _packBonusModelAndTooltipData(mainPackedBonusAndTooltipList, mainRewards, tooltipData)
    _packBonusModelAndTooltipData(otherPackedBonusAndTooltipList, otherRewards, tooltipData)
