# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions_30/bonus_sorter.py
import logging
import typing
from constants import PREMIUM_ENTITLEMENTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.customization.shared import getSingleVehicleForCustomization
from gui.impl import backport
from gui.impl.backport import TooltipData
from gui.impl.gen import R
from gui.server_events.awards_formatters import BATTLE_BONUS_X5_TOKEN, PM_POINTS_TOKEN
from gui.server_events.bonuses import SimpleBonus, ItemsBonus, TokensBonus, CrewBooksBonus, CustomizationsBonus, BlueprintsBonusSubtypes, TmanTemplateTokensBonus
from gui.server_events.finders import isPM3Points
from gui.server_events.formatters import parseComplexToken
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.gui_items import GUI_ITEM_TYPE, getItemTypeID
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.missions.packers.bonus import CustomizationBonusUIPacker, getLocalizedBonusName, DossierBonusUIPacker, DOSSIER_BADGE_ICON_PREFIX, DOSSIER_BADGE_POSTFIX, ItemBonusUIPacker, TokenBonusUIPacker, CrewBookBonusUIPacker, getDefaultBonusPackersMap, BonusUIPacker, SimpleBonusUIPacker, BlueprintBonusUIPacker, GoodiesBonusUIPacker, BACKPORT_TOOLTIP_CONTENT_ID, BaseBonusUIPacker
from gui.shared.money import Currency
from helpers import dependency
from items.components.c11n_constants import Rarity
from items.components.crew_books_constants import CREW_BOOK_RARITY
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
if typing.TYPE_CHECKING:
    from frameworks.wulf.view.array import Array
    from typing import List, Dict
    from gui.impl.gen.view_models.common.bonus_model import BonusModel
    from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel
    from gui.shared.gui_items.customization.c11n_items import Customization
_logger = logging.getLogger(__name__)
REWARDS_ORDER = (PM_POINTS_TOKEN,
 'vehicles',
 'premiumYear',
 Rarity.LEGENDARY,
 'campaignWithHonorBadge',
 Rarity.EPIC,
 'operationWithHonorBadge',
 'operationWithoutHonorBadge',
 Rarity.RARE,
 'crewSkins',
 'tankmen',
 '2DStyle',
 'decal',
 'projection_decal',
 'inscriptions',
 'emblems',
 Currency.GOLD,
 Currency.CRYSTAL,
 Currency.CREDITS,
 'freeXP',
 'premium',
 'improvedEquipment',
 'experimentalEquipment',
 Currency.EQUIP_COIN,
 CREW_BOOK_RARITY.UNIVERSAL,
 CREW_BOOK_RARITY.UNIVERSAL_GUIDE,
 'standardEquipment',
 BATTLE_BONUS_X5_TOKEN,
 'personalReserves',
 'blueprintsNational',
 'blueprintsUniversal',
 CREW_BOOK_RARITY.CREW_RARE,
 CREW_BOOK_RARITY.UNIVERSAL_BROCHURE,
 CREW_BOOK_RARITY.CREW_COMMON,
 'equipmentDirectives',
 'crewDirectives',
 'largeRepairkit',
 'autoExtinguishers',
 'largeMedkit',
 'slots')
LAST_ORDER = len(REWARDS_ORDER)

def getRewardOrder(rewardName):
    try:
        order = REWARDS_ORDER.index(rewardName)
    except ValueError:
        order = LAST_ORDER

    return order


def getNotificationBonusOrder(bonus):
    if bonus.isShowInGUI():
        packer = getBonusPacker()
        bonusList = packer.pack(bonus)
        for packedBonus in bonusList:
            if isinstance(packedBonus, list):
                return packedBonus[-1]
            return getRewardOrder(packedBonus.getName())

    return LAST_ORDER


def getBonusPacker(isRewardScreen=False):
    mapping = getDefaultBonusPackersMap()
    premiumPacker = PM3PremiumPacker()
    blueprintBonusPacker = PM3BlueprintBonusUIPacker()
    customizationPacker = PM3CustomizationBonusUIPacker() if isRewardScreen else PM3DashboardCustomizationBonusUIPacker()
    mapping.update({PREMIUM_ENTITLEMENTS.BASIC: premiumPacker,
     PREMIUM_ENTITLEMENTS.PLUS: premiumPacker,
     'blueprints': blueprintBonusPacker,
     'goodies': PM3GoodiesBonusUIPacker(),
     'tokens': PM3TokenBonusUIPacker(),
     'customizations': customizationPacker,
     'items': PM3ItemBonusUIPacker(),
     'dossier': PM3DossierBonusUIPacker(),
     'crewBooks': PM3CrewBookBonusUIPacker(),
     'tmanToken': PM3TmanTemplateBonusPacker()})
    return BonusUIPacker(mapping)


def packMissionsBonusModelAndTooltipData(bonuses, packer, model, tooltipData=None):
    bonusIndexTotal = 0
    if tooltipData is not None:
        bonusIndexTotal = len(tooltipData)
    totalBonusesList = []
    for bonus in bonuses:
        if bonus.isShowInGUI():
            bonusList = packer.pack(bonus)
            bonusTooltipList = packer.getToolTip(bonus)
            for packedBonus, bonusTooltip in zip(bonusList, bonusTooltipList):
                if isinstance(packedBonus, list):
                    packedBonus.append(bonusTooltip)
                    totalBonusesList.append(packedBonus)
                totalBonusesList.append((packedBonus, getRewardOrder(packedBonus.getName()), bonusTooltip))

    totalBonusesList.sort(key=lambda b: b[1])
    for bonusIndex, bonusData in enumerate(totalBonusesList):
        bonusData[0].setIndex(bonusIndexTotal)
        tooltipIdx = str(bonusIndexTotal)
        if hasattr(bonusData[0], 'setTooltipId'):
            bonusData[0].setTooltipId(tooltipIdx)
        model.addViewModel(bonusData[0])
        if tooltipData is not None:
            tooltipData[tooltipIdx] = totalBonusesList[bonusIndex][2]
        bonusIndexTotal += 1

    return


class PM3GoodiesBonusUIPacker(GoodiesBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for booster, count in sorted(bonus.getBoosters().iteritems(), key=lambda b: b[0].boosterID):
            if booster is None or not count:
                continue
            result.append([cls._packSingleBoosterBonus(bonus, booster, count), getRewardOrder('personalReserves')])

        for demountkit, count in sorted(bonus.getDemountKits().iteritems()):
            if demountkit is None or not count:
                continue
            result.append([cls._packSingleDemountKitBonus(bonus, demountkit, count), LAST_ORDER])

        for form, count in sorted(bonus.getRecertificationForms().iteritems()):
            if form is None or not count:
                continue
            result.append([cls._packRecertificationFormsBonus(bonus, form, count), LAST_ORDER])

        for item, count in sorted(bonus.getMentoringLicenses().iteritems()):
            if item is None or not count:
                continue
            result.append([cls._packMentorLicensesBonus(bonus, item, count), LAST_ORDER])

        return result


class PM3BlueprintBonusUIPacker(BlueprintBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(bonus.getCount()))
        model.setType(bonus.getBlueprintName())
        model.setIcon(bonus.getImageCategory())
        blueprintName = bonus.getBlueprintName()
        if blueprintName == BlueprintsBonusSubtypes.NATION_FRAGMENT:
            label = cls._getNationalLabel(bonus)
        else:
            label = bonus.getBlueprintTooltipName()
        model.setLabel(label)
        return [[model, cls._blueprintsChecker(bonus)]]

    @classmethod
    def _getNationalLabel(cls, bonus):
        nation = bonus.getImageCategory()
        nationName = backport.text(R.strings.blueprints.nations.dyn(nation)())
        return backport.text(R.strings.quests.bonusName.blueprints.nation(), nationName=nationName)

    @classmethod
    def _blueprintsChecker(cls, bonus):
        blueprintName = bonus.getBlueprintName()
        if blueprintName == BlueprintsBonusSubtypes.UNIVERSAL_FRAGMENT:
            return getRewardOrder('blueprintsUniversal')
        return getRewardOrder('blueprintsNational') if blueprintName == BlueprintsBonusSubtypes.NATION_FRAGMENT else LAST_ORDER


class PM3PremiumPacker(SimpleBonusUIPacker):
    __PREMIUM_YEAR = 360

    @classmethod
    def _pack(cls, bonus):
        label = getLocalizedBonusName(bonus.getName())
        return [[cls._packSingleBonus(bonus, label if label else ''), getRewardOrder('premiumYear') if bonus.getValue() >= cls.__PREMIUM_YEAR else getRewardOrder('premium')]]


class PM3DashboardCustomizationBonusUIPacker(CustomizationBonusUIPacker):
    __c11n = dependency.descriptor(ICustomizationService)

    @classmethod
    def _pack(cls, bonus):
        result = []
        for item in bonus.getCustomizations():
            if item is None:
                continue
            label = getLocalizedBonusName(bonus.getC11nItem(item).itemTypeName)
            result.append([cls._packSingleBonus(bonus, item, label if label else ''), cls._customizationsChecker(item)])

        return result

    @classmethod
    def _customizationsChecker(cls, item):
        itemTypeName = item.get('custType')
        itemID = item.get('id')
        itemTypeID = getItemTypeID(itemTypeName)
        customizationBonus = cls.__c11n.getItemByID(itemTypeID, itemID)
        if customizationBonus.itemTypeName == 'style' and not customizationBonus.is3D:
            return getRewardOrder('2DStyle')
        return getRewardOrder(customizationBonus.rarity) if customizationBonus.itemTypeName == 'attachment' else getRewardOrder(itemTypeName)

    @classmethod
    def _getToolTipData(cls, itemCustomization):
        specialAlias = TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD
        specialArgs = CustomizationTooltipContext(itemCD=itemCustomization.intCD)
        if itemCustomization.itemTypeName in ('camouflage', 'style'):
            vehicle = getSingleVehicleForCustomization(itemCustomization)
            if vehicle is not None:
                specialAlias = TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM
                specialArgs = CustomizationTooltipContext(itemCD=itemCustomization.intCD, vehicleIntCD=vehicle)
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=specialAlias, specialArgs=specialArgs)


class PM3CustomizationBonusUIPacker(PM3DashboardCustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        c11nItem = bonus.getC11nItem(item)
        model.setValue(str(item.get('value', 0)))
        icon = str(c11nItem.itemTypeName)
        if c11nItem.itemTypeName == 'style':
            label = c11nItem.userName
            icon = str(item.get('id'))
        if c11nItem.itemTypeName == 'attachment':
            label = backport.text(R.strings.item_types.customization.attachment.rarity(), rarity=backport.text(R.strings.vehicle_customization.customization.rarity.dyn(c11nItem.rarity)()))
            icon = c11nItem.name
            model.setName(c11nItem.itemTypeName)
        model.setIcon(icon)
        model.setLabel(label)
        return model


class PM3DossierBonusUIPacker(DossierBonusUIPacker):

    @classmethod
    def _packAchievements(cls, bonus):
        return [ [cls._packSingleAchievement(achievement, bonus), LAST_ORDER] for achievement in bonus.getAchievements() ]

    @classmethod
    def _packBadges(cls, bonus):
        result = []
        for badge in bonus.getBadges():
            dossierIconName = DOSSIER_BADGE_ICON_PREFIX + str(badge.badgeID)
            dossierValue = 0
            dossierLabel = badge.getUserName()
            result.append([cls._packSingleBonus(bonus, dossierIconName, DOSSIER_BADGE_POSTFIX, dossierValue, dossierLabel), cls._dossierChecker(badge)])

        return result

    @staticmethod
    def _dossierChecker(badge):
        if badge.getName().startswith('personal_missions_3'):
            if badge.getName().endswith('all'):
                return getRewardOrder('campaignWithHonorBadge')
            if badge.getName().endswith('1'):
                return getRewardOrder('operationWithoutHonorBadge')
            if badge.getName().endswith('2'):
                return getRewardOrder('operationWithHonorBadge')
        return LAST_ORDER


class PM3ItemBonusUIPacker(ItemBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        bonusItems = bonus.getItems()
        result = []
        for item, count in sorted(bonusItems.iteritems(), key=cls._itemsSortFunction):
            if item is None or not count:
                continue
            result.append([cls._packSingleBonus(bonus, item, count), cls._itemsChecker(item)])

        return result

    @staticmethod
    def _itemsChecker(item):
        if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
            if item.isModernized:
                return getRewardOrder('improvedEquipment')
            if item.isDeluxe:
                return getRewardOrder('experimentalEquipment')
            return getRewardOrder('standardEquipment')
        if item.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT:
            return getRewardOrder(item.name)
        if item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
            if item.isCrewBooster():
                return getRewardOrder('crewDirectives')
            return getRewardOrder('equipmentDirectives')
        return LAST_ORDER


class PM3TokenBonusUIPacker(TokenBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        bonusTokens = bonus.getTokens()
        result = []
        bonusPackers = cls._getTokenBonusPackers()
        for tokenID, token in bonusTokens.iteritems():
            complexToken = parseComplexToken(tokenID)
            tokenType = cls._getTokenBonusType(tokenID, complexToken)
            specialPacker = bonusPackers.get(tokenType)
            if specialPacker is None:
                continue
            packedBonus = cls._packToken(specialPacker, bonus, complexToken, token)
            if packedBonus is not None:
                result.append([packedBonus, cls._tokensChecker(token)])

        return result

    @staticmethod
    def _tokensChecker(token):
        if isPM3Points(token.id):
            return getRewardOrder(PM_POINTS_TOKEN)
        return getRewardOrder(BATTLE_BONUS_X5_TOKEN) if token.id.startswith(BATTLE_BONUS_X5_TOKEN) else LAST_ORDER


class PM3CrewBookBonusUIPacker(CrewBookBonusUIPacker):
    __itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def _pack(cls, bonus):
        result = []
        for book, count in sorted(bonus.getItems(), key=lambda b: b[0].nationID):
            if book is None or not count:
                continue
            result.append([cls._packSingleBonus(bonus, book, count), cls._crewBooksChecker(book)])

        return result

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for item, count in sorted(bonus.getItems(), key=lambda b: b[0].nationID):
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.CREW_BOOK, specialArgs=[item.intCD, count]))

        return tooltipData

    @classmethod
    def _crewBooksChecker(cls, book):
        crewBook = cls.__itemsCache.items.getItemByCD(book.intCD)
        return getRewardOrder(crewBook.getBookType()) if crewBook is not None else LAST_ORDER


class PM3TmanTemplateBonusPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                packed = cls.__packTmanTemplateToken(tokenID, bonus)
                if packed is None:
                    _logger.error('Received wrong tman_template token from server: %s', tokenID)
                else:
                    result.append([packed, getRewardOrder('tankmen')])

        return result

    @classmethod
    def __packTmanTemplateToken(cls, tokenID, bonus):
        recruitInfo = getRecruitInfo(tokenID)
        if recruitInfo is None:
            return
        else:
            if 'pm3' in recruitInfo.getGroupName():
                bonusImageName = 'tankman_' + recruitInfo.getGroupName().split('_', 1)[1]
            else:
                bonusImageName = 'tankman'
            tankManFullName = recruitInfo.getFullUserName()
            model = IconBonusModel()
            cls._packCommon(bonus, model)
            model.setName(bonusImageName)
            model.setIcon(bonusImageName)
            model.setLabel(tankManFullName)
            return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for tokenID in bonus.getTokens():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, specialArgs=[tokenID]))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        return [ BACKPORT_TOOLTIP_CONTENT_ID for tokenID in bonus.getTokens() if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX) ]
