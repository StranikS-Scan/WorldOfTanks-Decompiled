# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_bonuses_helpers.py
from collections import namedtuple, OrderedDict, defaultdict
from copy import deepcopy
from itertools import izip_longest
import typing
from constants import PREMIUM_ENTITLEMENTS, MAX_VEHICLE_LEVEL
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import MERGED_BONUS_NAME, LootBoxBonusComposer
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import CrewBonusTypes, preparationRewardsCurrency, checkAndFillVehicles, checkAndFillCustomizations, checkAndFillTokens, checkAndFillItems
from gui.impl.backport import TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.views.lobby.new_year.components.reward_item_model import RewardItemModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.bundle_reward_item_model import BundleRewardItemModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.sack_reward_model import SackRewardModel
from gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.bonus_items_names import BonusItemsNames
from gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.loot_box_reward_row_model import LootBoxRewardRowModel
from gui.impl.gen.view_models.views.loot_box_view.loot_congrats_types import LootCongratsTypes
from gui.impl.new_year.new_year_bonus_packer import NewYearTmanTemplateBonusPacker, packBonusModelAndTooltipData, NYPremVehiclesBonusUIPacker, NYToyBonusUIPackerExtra, NYToyBonusUIPacker
from gui.server_events.awards_formatters import AWARDS_SIZES, EPIC_AWARD_SIZE, getLootboxesAutoOpenAwardsPacker, getNYAwardsPacker, getNYEpicAwardsPacker
from gui.server_events.bonuses import getNonQuestBonuses, SimpleBonus, splitBonuses
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.missions.packers.bonus import BaseBonusUIPacker, getDefaultBonusPackersMap, BonusUIPacker, Customization3Dand2DbonusUIPacker, SimpleBonusUIPacker, VEHICLE_RENT_ICON_POSTFIX, CustomizationBonusUIPacker, getLocalizedBonusName, ItemBonusUIPacker, BACKPORT_TOOLTIP_CONTENT_ID
from gui.shared.money import Currency
from helpers import dependency
from items import parseIntCompactDescr, ITEM_TYPE_INDICES, EQUIPMENT_TYPES
from items.components.ny_constants import CurrentNYConstants
from items.components.ny_constants import NyCurrency, RewartKitSettings
from items.vehicles import getItemByCompactDescr
from new_year.ny_constants import GuestsQuestsTokens
from shared_utils import first
from skeletons.new_year import INewYearController
AWARDS_MAX_COUNT = 6
MULTIOPEN_AWARDS_MAX_COUNT = 6
_BONUSES_ORDER = (Currency.GOLD,
 Currency.CREDITS,
 Currency.CRYSTAL,
 'tankmen',
 PREMIUM_ENTITLEMENTS.PLUS,
 PREMIUM_ENTITLEMENTS.BASIC,
 'freeXP',
 'freeXPFactor',
 'creditsFactor',
 'items',
 'berths',
 'dossier',
 'goodies',
 'tokens',
 'blueprints',
 'crewSkins',
 CrewBonusTypes.CREW_BOOK_BONUSES,
 CrewBonusTypes.CREW_SKIN_BONUSES,
 'finalBlueprints',
 'customizations',
 'vehicles',
 'slots',
 'modernizedEquipment',
 CurrentNYConstants.TOYS)
NEWYEAR_BONUS_ORDER = (NyCurrency.CRYSTAL,
 NyCurrency.EMERALD,
 NyCurrency.AMBER,
 NyCurrency.IRON) + _BONUSES_ORDER
CHRISTMAS_BONUS_ORDER = (NyCurrency.EMERALD,
 NyCurrency.CRYSTAL,
 NyCurrency.AMBER,
 NyCurrency.IRON) + _BONUSES_ORDER
ORIENTAL_BONUS_ORDER = (NyCurrency.AMBER,
 NyCurrency.CRYSTAL,
 NyCurrency.EMERALD,
 NyCurrency.IRON) + _BONUSES_ORDER
FAIRYTALE_BONUS_ORDER = (NyCurrency.IRON,
 NyCurrency.CRYSTAL,
 NyCurrency.EMERALD,
 NyCurrency.AMBER) + _BONUSES_ORDER
ORDER_BY_BOX_TYPE = {RewartKitSettings.NEW_YEAR: NEWYEAR_BONUS_ORDER,
 RewartKitSettings.CHRISTMAS: CHRISTMAS_BONUS_ORDER,
 RewartKitSettings.ORIENTAL: ORIENTAL_BONUS_ORDER,
 RewartKitSettings.FAIRYTALE: FAIRYTALE_BONUS_ORDER}
AUTO_OPEN_OTHER_ORDER = (Currency.GOLD,
 Currency.CREDITS,
 PREMIUM_ENTITLEMENTS.PLUS,
 PREMIUM_ENTITLEMENTS.BASIC,
 'freeXP',
 Currency.EQUIP_COIN,
 'customizations',
 CrewBonusTypes.CREW_BOOK_BONUSES,
 'common',
 'battle_bonus_x5',
 'booster_credits',
 'booster_xp',
 'booster_xp_premium',
 'booster_free_xp_and_crew_xp',
 'booster_free_xp_and_crew_xp_premium',
 'goodies',
 'items',
 'largeRepairkit',
 'largeMedkit',
 'autoExtinguishers',
 'smallRepairkit',
 'smallMedkit',
 'handExtinguishers',
 'slots')
_GROUPED_SORT_C11N_INDEX = ('style_3d', 'style', 'projectionDecal', 'decal', 'emblem', 'inscription', 'insignia', 'personalNumber', 'paint')
_COMMON_BONUSES_ORDER = ({'getName': 'premium_plus'},
 {'getName': 'gold'},
 {'getName': 'credits'},
 {'getName': 'slots'})
RewardsGroup = namedtuple('RewardsGroup', ('name', 'bonusTypes', 'bonuses', 'filterFuncs', 'sortKeyFunc'))

def isOptionalDevice(itemTypeID, _):
    return itemTypeID == ITEM_TYPE_INDICES['optionalDevice']


def isBattleBooster(itemTypeID, itemCD):
    if itemTypeID != ITEM_TYPE_INDICES['equipment']:
        return False
    itemDescr = getItemByCompactDescr(itemCD)
    return itemDescr.equipmentType == EQUIPMENT_TYPES.battleBoosters


def isCrewBook(itemTypeID, _):
    return itemTypeID == ITEM_TYPE_INDICES['crewBook']


def getItemsFilter(conditions):

    def itemsFilter(items):
        filtered = {}
        for itemCD, count in items.items():
            itemTypeID, _, _ = parseIntCompactDescr(itemCD)
            if any((condition(itemTypeID, itemCD) for condition in conditions)):
                filtered[itemCD] = count
                del items[itemCD]

        return filtered

    return itemsFilter


def compareVehicles(zipped):
    bonusModel, _, __ = zipped
    sortIndex = MAX_VEHICLE_LEVEL - bonusModel.getVehicleLvl()
    if VEHICLE_RENT_ICON_POSTFIX in bonusModel.getName():
        sortIndex += MAX_VEHICLE_LEVEL
    elif bonusModel.getIsCompensation():
        sortIndex += MAX_VEHICLE_LEVEL * 2
    return sortIndex


def compareCustomization(zipped):
    bonusModel, _, __ = zipped
    iconName = bonusModel.getIcon()
    return _GROUPED_SORT_C11N_INDEX.index(iconName) if iconName in _GROUPED_SORT_C11N_INDEX else len(_GROUPED_SORT_C11N_INDEX)


def compareCommonBonuses(zippedBonus):
    for index, criteria in enumerate(_COMMON_BONUSES_ORDER):
        for method, value in criteria.items():
            bonus, _, __ = zippedBonus
            if not hasattr(bonus, method) or value not in getattr(bonus, method)():
                break
        else:
            return index

    return len(_COMMON_BONUSES_ORDER)


def compareOtherBonuses(zippedBonus):
    bonus, _, __ = zippedBonus
    bonusName = bonus.getName()
    if bonusName in AUTO_OPEN_OTHER_ORDER:
        if bonusName == 'items' and bonus.getItem() in AUTO_OPEN_OTHER_ORDER:
            return AUTO_OPEN_OTHER_ORDER.index(bonus.getItem())
        if bonusName == 'goodies' and bonus.getIcon() in AUTO_OPEN_OTHER_ORDER:
            return AUTO_OPEN_OTHER_ORDER.index(bonus.getIcon())
        return AUTO_OPEN_OTHER_ORDER.index(bonusName)
    return len(AUTO_OPEN_OTHER_ORDER)


class MergedBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        model = IconBonusModel()
        cls._packCommon(bonus, model)
        model.setName('default')
        model.setValue(backport.text(R.strings.quests.missions.awards.merged(), count=len(bonus.getValue())))
        return [model]

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = backport.createTooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.ADDITIONAL_AWARDS, specialArgs=cls._getShortBonusesData(bonus.getValue()))
        return [tooltipData]

    @classmethod
    def _getShortBonusesData(cls, bonuses):
        result = []
        formatter = getLootboxesAutoOpenAwardsPacker()
        for bonus in formatter.format(bonuses):
            shortData = {'name': bonus.userName,
             'label': bonus.getFormattedLabel(),
             'imgSource': bonus.getImage(AWARDS_SIZES.BIG),
             'highlightIcon': bonus.getHighlightIcon(AWARDS_SIZES.BIG),
             'overlayIcon': bonus.getOverlayIcon(AWARDS_SIZES.BIG)}
            result.append(shortData)

        return result


class NYCustomization3Dand2DbonusUIPacker(Customization3Dand2DbonusUIPacker):
    _STYLE_BONUS_NAME = 'style'

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        packed = super(NYCustomization3Dand2DbonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        customization = bonus.getC11nItem(item)
        count = int(item.get('value', 0))
        if count > 1:
            value = backport.text(R.strings.ny.lootBoxAutoOpen.reward.customization.label(), name=customization.userName, quantity=count)
        else:
            value = customization.userName
        packed.setValue(value)
        return packed

    @classmethod
    def _packStyle(cls, packed, is3Dstyle):
        super(NYCustomization3Dand2DbonusUIPacker, cls)._packStyle(packed, is3Dstyle)
        packed.setName(cls._3D_STYLE_ICON_NAME if is3Dstyle else cls._STYLE_BONUS_NAME)


class NYCustomizationCollapsed3Dand2DbonusUIPacker(NYCustomization3Dand2DbonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        mergedBonuses = cls.__preformat(bonus)
        result = []
        for cItems in mergedBonuses:
            cItem = first(cItems)
            customization = bonus.getC11nItem(cItem)
            label = getLocalizedBonusName(customization.itemTypeName)
            model = cls._packSingleBonus(bonus, cItem, label if label else '')
            mergedLen = len(cItems)
            value = mergedLen if mergedLen > 1 else cItem.get('value', 0)
            if customization.itemTypeName == 'style':
                value = customization.userName
            model.setValue(str(value))
            result.append(model)

        return result

    @classmethod
    def _getToolTip(cls, bonus):
        mergedBonuses = cls.__preformat(bonus)
        tooltipData = []
        for cItems in mergedBonuses:
            cItem = first(cItems)
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD, specialArgs=CustomizationTooltipContext(itemCD=bonus.getC11nItem(cItem).intCD)))

        return tooltipData

    @staticmethod
    def __preformat(bonus):
        preformated = defaultdict(list)
        for cItem in bonus.getCustomizations():
            if cItem is None:
                continue
            itemTypeID = bonus.getC11nItem(cItem).id
            preformated[itemTypeID].append(cItem)

        return preformated.values()


class NyBattleTokensPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        models = []
        for tokenID in bonus.getTokens().iterkeys():
            model = cls._packSingleBonus(tokenID)
            if model is not None:
                models.append(model)

        return models

    @classmethod
    def _packSingleBonus(cls, tokenID):
        model = None
        if tokenID == GuestsQuestsTokens.TOKEN_CAT:
            model = cls._getBonusModel()
            model.setName(GuestsQuestsTokens.GUEST_C)
            model.setValue(str(backport.text(R.strings.ny.guestC.name())))
        return model

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.new_year.tooltips.NyRewardKitGuestCTooltip()]


class NyCurrenciesBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        model = cls._getBonusModel()
        model.setValue(str(bonus.getValue()))
        model.setName(str(bonus.getCode()))
        return [model]

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.new_year.tooltips.NyResourceTooltip()] if bonus.getCode() in NyCurrency.ALL else [BACKPORT_TOOLTIP_CONTENT_ID]


def getNYLootBoxBonusPacker(isExtra=False):
    mapping = getDefaultBonusPackersMap()
    mapping.update({'vehicles': NYPremVehiclesBonusUIPacker(),
     'customizations': NYCustomizationCollapsed3Dand2DbonusUIPacker(),
     MERGED_BONUS_NAME: MergedBonusUIPacker(),
     CurrentNYConstants.TOYS: NYToyBonusUIPackerExtra() if isExtra else NYToyBonusUIPacker(),
     'tmanToken': NewYearTmanTemplateBonusPacker(),
     'currencies': NyCurrenciesBonusPacker(),
     'battleToken': NyBattleTokensPacker(),
     'items': NyItemBonusUIPacker()})
    return BonusUIPacker(mapping)


def packBonusGroups(bonuses, groupModelsList, groupsLayout, packer, tooltipsData=None):
    __groupBonuses(bonuses, groupsLayout)
    groupModelsList.clear()
    for group in groupsLayout:
        groupBonuses, _ = getLootboxBonuses(group.bonuses)
        if not groupBonuses:
            continue
        groupModel = LootBoxRewardRowModel()
        bonusModelsList = groupModel.rewards
        groupModel.setLabel(backport.text(group.name))
        bonusesCount = packBonusModelAndTooltipData(groupBonuses, bonusModelsList, packer, tooltipsData, sortKey=group.sortKeyFunc)
        if not bonusesCount:
            continue
        groupModel.setRewardsCount(bonusesCount)
        if not group.bonusTypes:
            groupModel.setBonusType(BonusItemsNames.OTHER)
        bonusModelsList.invalidate()
        groupModelsList.addViewModel(groupModel)

    groupModelsList.invalidate()


def getFormattedLootboxBonuses(rewards, maxAwardCount):
    bonuses, alwaysVisibleBonuses, specialRewardType = __getLootboxBonusesData(rewards)
    __preformatBonuses(bonuses)
    __preformatBonuses(alwaysVisibleBonuses)
    formatter = LootBoxBonusComposer(maxAwardCount, getNYAwardsPacker())
    formattedBonuses = formatter.getVisibleFormattedBonuses(bonuses, alwaysVisibleBonuses, size=AWARDS_SIZES.BIG)
    return (formattedBonuses, specialRewardType)


def getEpicFormattedLootboxBonuses(rewards, maxAwardCount, sortKey):
    bonuses, alwaysVisibleBonuses, specialRewardType = __getLootboxBonusesData(rewards)
    __preformatBonuses(bonuses, sortKey=sortKey)
    __preformatBonuses(alwaysVisibleBonuses)
    formatter = LootBoxBonusComposer(maxAwardCount, getNYEpicAwardsPacker())
    formattedBonuses = formatter.getVisibleFormattedBonuses(bonuses, alwaysVisibleBonuses, size=EPIC_AWARD_SIZE)
    return (formattedBonuses, specialRewardType)


def getLootboxBonuses(rewards, maxAwardCount=None, sortKey=None):
    bonuses, alwaysVisibleBonuses, specialRewardType = __getLootboxBonusesData(rewards)
    if maxAwardCount is not None:
        bonuses = __composeBonuses(bonuses, alwaysVisibleBonuses, maxAwardCount)
    else:
        bonuses += alwaysVisibleBonuses
    __preformatBonuses(bonuses, sortKey=sortKey)
    return (bonuses, specialRewardType)


def __getLootboxBonusesData(rewards):
    preparationRewardsCurrency(rewards)
    specialRewardType = ''
    bonuses = []
    alwaysVisibleBonuses = []
    for rewardType, rewardValue in rewards.iteritems():
        if rewardType == 'vehicles' and isinstance(rewardValue, list):
            for vehicleData in rewardValue:
                bonus = getNonQuestBonuses(rewardType, vehicleData)
                if checkAndFillVehicles(bonus, alwaysVisibleBonuses, bonuses, onlyVideoVehicle=False):
                    specialRewardType = LootCongratsTypes.CONGRAT_TYPE_VEHICLE

        if rewardType == 'customizations':
            bonus = getNonQuestBonuses(rewardType, rewardValue)
            if checkAndFillCustomizations(bonus, alwaysVisibleBonuses, bonuses):
                specialRewardType = LootCongratsTypes.CONGRAT_TYPE_STYLE
        if rewardType == 'tokens':
            bonus = getNonQuestBonuses(rewardType, rewardValue)
            specialRewardType = checkAndFillTokens(bonus, alwaysVisibleBonuses, bonuses)
        if rewardType == 'blueprints':
            bonuses += getNonQuestBonuses(rewardType, rewardValue, ctx={'isPacked': True})
        if rewardType == 'slots' and 'vehicles' in rewards:
            alwaysVisibleBonuses += getNonQuestBonuses(rewardType, rewardValue)
        if rewardType == 'items':
            bonus = getNonQuestBonuses(rewardType, rewardValue)
            specialRewardType = checkAndFillItems(bonus, alwaysVisibleBonuses, bonuses)
        bonuses += getNonQuestBonuses(rewardType, rewardValue)

    return (bonuses, alwaysVisibleBonuses, specialRewardType)


def __bonusesOrderKey(bonus):
    name = bonus.getName()
    key = _BONUSES_ORDER.index(name) if name in _BONUSES_ORDER else len(_BONUSES_ORDER)
    return key


def __handlePremiumTankSpecialCase(bonuses):
    premiumTankIndex = -1
    slotsIndex = -1
    for bonus in bonuses:
        if bonus.getName() == 'vehicles':
            premiumTankIndex = bonuses.index(bonus)
        if bonus.getName() == 'slots':
            slotsIndex = bonuses.index(bonus)

    if premiumTankIndex > -1:
        slotBonus = bonuses.pop(slotsIndex)
        bonuses.insert(premiumTankIndex, slotBonus)


def __composeBonuses(bonuses, alwaysVisibleBonuses, maxAwardCount):
    bonuses = splitBonuses(bonuses)
    alwaysVisibleBonuses = splitBonuses(alwaysVisibleBonuses)
    if len(bonuses) + len(alwaysVisibleBonuses) > maxAwardCount:
        bonusesLimit = max(0, maxAwardCount - len(alwaysVisibleBonuses) - 1)
        mergedBonus = SimpleBonus(MERGED_BONUS_NAME, bonuses[bonusesLimit:])
        return bonuses[:bonusesLimit] + alwaysVisibleBonuses + [mergedBonus]
    return bonuses + alwaysVisibleBonuses


@dependency.replace_none_kwargs(nyController=INewYearController)
def __getToysSortedByRankAndCount(toys, nyController=None):
    orderedToys = OrderedDict()
    toysDescriptors = [ (nyController.getToyDescr(toyId), count) for toyId, count in toys.iteritems() ]
    sortedToysDescriptors = sorted(toysDescriptors, cmp=__compareToysByRankAndCount, reverse=True)
    for toyDesc, count in sortedToysDescriptors:
        orderedToys[toyDesc.id] = count

    return orderedToys


def __compareToysByRankAndCount(toy1, toy2):
    toyADesc, toyACount = toy1
    toyBDesc, toyBCount = toy2
    return cmp((toyADesc.rank, toyACount), (toyBDesc.rank, toyBCount))


def __preformatBonuses(bonuses, sortKey=None):
    sortKey = sortKey or __bonusesOrderKey
    bonuses.sort(key=sortKey)


def __groupBonuses(bonuses, groupsLayout):
    bonuses = deepcopy(bonuses)
    for group in groupsLayout:
        if not group.bonusTypes:
            group.bonuses.update(bonuses)
            bonuses.clear()
        filterFuncs = group.filterFuncs or ()
        for bonusType, filterFunc in izip_longest(group.bonusTypes, filterFuncs):
            if bonusType not in bonuses:
                continue
            if filterFunc is None:
                group.bonuses[bonusType] = bonuses.pop(bonusType)
            bonus = bonuses[bonusType]
            filtered = filterFunc(bonus)
            if filtered:
                group.bonuses[bonusType] = filtered
            if not bonus:
                del bonuses[bonusType]

        if not bonuses:
            break

    return


class _NYSackCustomizationBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(_NYSackCustomizationBonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        customization = bonus.getC11nItem(item)
        model.setLabel(customization.userName)
        model.setIntCD(customization.intCD)
        return model

    @classmethod
    def _getBonusModel(cls):
        return BundleRewardItemModel()

    @classmethod
    def _createBonusModel(cls):
        return BundleRewardItemModel()


class _NYSackRandomBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus, '')]

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.new_year.tooltips.NySackRandomRewardTooltip()]


class NyItemBonusUIPacker(ItemBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, count):
        model = RewardItemModel()
        cls._packCommon(bonus, model)
        model.setValue(str(count))
        model.setIcon(item.getGUIEmblemID())
        model.setOverlayType(item.getOverlayType())
        model.setLabel(item.userName)
        model.setItem(item.getGUIEmblemID())
        return model


def getNYSackBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'customizations': _NYSackCustomizationBonusUIPacker(),
     'randomNyBooklet': _NYSackRandomBonusUIPacker(),
     'randomNyGuide': _NYSackRandomBonusUIPacker(),
     'randomNyInstruction': _NYSackRandomBonusUIPacker(),
     'randomNy24Toy': _NYSackRandomBonusUIPacker()})
    return BonusUIPacker(mapping)


class _NYSackRewardCustomizationBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(_NYSackRewardCustomizationBonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        customization = bonus.getC11nItem(item)
        model.setLabel(customization.userName)
        model.setItemType(customization.itemTypeName)
        count = int(item.get('value', 0))
        if count > 1:
            model.setValue(str(count))
        return model

    @classmethod
    def _getBonusModel(cls):
        return SackRewardModel()

    @classmethod
    def _createBonusModel(cls):
        return SackRewardModel()


def getNYSackRewardBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'customizations': _NYSackRewardCustomizationBonusUIPacker(),
     CurrentNYConstants.TOYS: NYToyBonusUIPacker()})
    return BonusUIPacker(mapping)
