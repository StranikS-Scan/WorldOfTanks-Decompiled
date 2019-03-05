# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/bonuses.py
import copy
from collections import namedtuple
from functools import partial
import BigWorld
from blueprints.BlueprintTypes import BlueprintTypes
from blueprints.FragmentTypes import getFragmentType
from constants import EVENT_TYPE as _ET, DOSSIER_TYPE, LOOTBOX_TOKEN_PREFIX
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from dossiers2.custom.records import RECORD_DB_IDS
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK, BADGES_BLOCK
from gui import makeHtmlString
from gui.Scaleform.genConsts.BOOSTER_CONSTANTS import BOOSTER_CONSTANTS
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.Scaleform.genConsts.TEXT_ALIGN import TEXT_ALIGN
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.BADGE import BADGE
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.Scaleform.settings import getBadgeIconPath, BADGES_ICONS, ICONS_SIZES
from gui.server_events.formatters import parseComplexToken
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_INDICES
from gui.shared.gui_items.Tankman import getRoleUserName, calculateRoleLevel, Tankman
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from gui.shared.money import Currency, Money
from gui.shared.utils.functions import makeTooltip, stripColorTagDescrTags
from helpers import dependency
from helpers import getLocalizedData, i18n
from helpers import time_utils
from helpers.i18n import makeString as _ms
from items import vehicles, tankmen
from items.components import c11n_components as cc
from items.components.crewSkins_constants import NO_CREW_SKIN_ID
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from personal_missions import PM_BRANCH, PM_BRANCH_TO_FREE_TOKEN_NAME
from shared_utils import makeTupleByDict, CONST_CONTAINER
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.shared.utils.requesters.blueprints_requester import getFragmentNationID, getVehicleCDForNational
from gui.shared.utils.requesters.blueprints_requester import getVehicleCDForIntelligence
from gui.shared.utils.requesters.blueprints_requester import makeNationalCD, makeIntelligenceCD
DEFAULT_CREW_LVL = 50
_CUSTOMIZATIONS_SCALE = 44.0 / 128
_EPIC_AWARD_STATIC_VO_ENTRIES = {'compensationTooltip': QUESTS.BONUSES_COMPENSATION,
 'hasCompensation': False,
 'highlightType': '',
 'overlayType': ''}
_ZERO_COMPENSATION_MONEY = Money(credits=0, gold=0)

def _getAchievement(block, record, value):
    if block == ACHIEVEMENT_BLOCK.RARE:
        record = value
        value = 0
    try:
        achieve = getAchievementFactory((block, record)).create(value=value)
        if achieve.isAvailableInQuest():
            return achieve
    except Exception:
        LOG_ERROR('There is error while getting bonus dossier record name')
        LOG_CURRENT_EXCEPTION()

    return None


def _isAchievement(block):
    return block in ACHIEVEMENT_BLOCK.ALL


def _isBadge(block):
    return block == BADGES_BLOCK


class SimpleBonus(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, name, value, isCompensation=False, ctx=None, compensationReason=None):
        self._name = name
        self._value = value
        self._isCompensation = isCompensation
        self._ctx = ctx or {}
        self._compensationReason = compensationReason

    def getName(self):
        return self._name

    def getValue(self):
        return self._value

    def setValue(self, value):
        self._value = value

    def isCompensation(self):
        return self._isCompensation

    def getCompensationReason(self):
        return self._compensationReason

    def getContext(self):
        return self._ctx

    def formatValue(self):
        return str(self._value) if self._value else None

    def format(self):
        return self._format(styleSubset='bonuses')

    def carouselFormat(self):
        return self._format(styleSubset='carouselBonuses')

    def formattedList(self):
        formattedObj = self.format()
        return [formattedObj] if formattedObj else []

    def isShowInGUI(self):
        return True

    def getIcon(self):
        pass

    def getTooltipIcon(self):
        pass

    def getTooltip(self):
        return _getItemTooltip(self._name)

    def getDescription(self):
        return i18n.makeString('#quests:bonuses/%s/description' % self._name, value=self.formatValue())

    def getList(self):
        return None

    def getWrappedEpicBonusList(self):
        return [{'id': 0,
          'type': 'custom/{}'.format(self.getName()),
          'value': self.getValue(),
          'icon': {AWARDS_SIZES.SMALL: self.getIconBySize(AWARDS_SIZES.SMALL),
                   AWARDS_SIZES.BIG: self.getIconBySize(AWARDS_SIZES.BIG)}}]

    def __getCommonAwardsVOs(self, iconSize='small', align=TEXT_ALIGN.CENTER, withCounts=False):
        itemInfo = {'imgSource': self.getIconBySize(iconSize),
         'label': self.getIconLabel(),
         'tooltip': self.getTooltip(),
         'align': align}
        if withCounts:
            if isinstance(self._value, int):
                itemInfo['count'] = self._value
            else:
                itemInfo['count'] = 1
        return itemInfo

    def getRankedAwardVOs(self, iconSize='small', withCounts=False, withKey=False):
        itemInfo = self.__getCommonAwardsVOs(iconSize=iconSize, withCounts=withCounts)
        if withKey:
            itemInfo['itemKey'] = self.getName()
        return [itemInfo]

    def getEpicAwardVOs(self, withDescription=False, iconSize='big', withCounts=False):
        itemInfo = self.__getCommonAwardsVOs(iconSize, align=TEXT_ALIGN.CENTER, withCounts=withCounts)
        itemInfo.update(_EPIC_AWARD_STATIC_VO_ENTRIES)
        if withDescription:
            itemInfo['title'] = i18n.makeString(TOOLTIPS.getAwardHeader(self._name))
            itemInfo['description'] = i18n.makeString(TOOLTIPS.getAwardBody(self._name))
        return [itemInfo]

    def getIconBySize(self, size):
        iconName = RES_ICONS.getBonusIcon(size, self.getName())
        if iconName is None:
            iconName = RES_ICONS.getBonusIcon(size, 'default')
        return iconName

    def getIconLabel(self):
        return text_styles.hightlight('x{}'.format(self.getValue()))

    def hasIconFormat(self):
        return False

    def _format(self, styleSubset):
        formattedValue = self.formatValue()
        if self._name is not None and formattedValue is not None:
            text = makeHtmlString('html_templates:lobby/quests/{}'.format(styleSubset), self._name, {'value': formattedValue})
            if text != self._name:
                return text
        return formattedValue


class IntegralBonus(SimpleBonus):

    def getCount(self):
        return int(self._value)

    def formatValue(self):
        return BigWorld.wg_getIntegralFormat(self._value) if self._value else None


class FloatBonus(SimpleBonus):

    def formatValue(self):
        return BigWorld.wg_getNiceNumberFormat(self._value) if self._value else None


class CountableIntegralBonus(IntegralBonus):
    pass


class CreditsBonus(IntegralBonus):

    def getIcon(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_1

    def getTooltipIcon(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARD_CREDITS

    def getList(self):
        return [{'value': self.formatValue(),
          'itemSource': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_CREDITS,
          'tooltip': TOOLTIPS.AWARDITEM_CREDITS}]

    def hasIconFormat(self):
        return True

    def getIconLabel(self):
        return text_styles.credits(self.getValue())


class GoldBonus(SimpleBonus):

    def formatValue(self):
        return BigWorld.wg_getGoldFormat(self._value) if self._value else None

    def getIcon(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_1

    def getList(self):
        return [{'value': self.formatValue(),
          'itemSource': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_GOLD,
          'tooltip': TOOLTIPS.AWARDITEM_GOLD}]

    def hasIconFormat(self):
        return True

    def getIconLabel(self):
        return text_styles.gold(self.getValue())


class CrystalBonus(IntegralBonus):

    def getIcon(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_CRYSTALICONBIG

    def getList(self):
        return [{'value': self.formatValue(),
          'itemSource': RES_ICONS.MAPS_ICONS_LIBRARY_CRYSTALICONBIG,
          'tooltip': TOOLTIPS.AWARDITEM_CRYSTAL}]

    def hasIconFormat(self):
        return True

    def getIconLabel(self):
        return text_styles.crystal(self.getValue())


class FreeXpBonus(IntegralBonus):

    def getList(self):
        return [{'value': self.formatValue(),
          'itemSource': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_FREEEXP,
          'tooltip': TOOLTIPS.AWARDITEM_FREEXP}]

    def hasIconFormat(self):
        return True

    def getIconLabel(self):
        return text_styles.hightlight(self.getValue())


class PremiumDaysBonus(IntegralBonus):

    def getList(self):
        return [{'itemSource': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_PREMIUM_1,
          'tooltip': TOOLTIPS.AWARDITEM_PREMIUM}]

    def hasIconFormat(self):
        return True

    def getIconBySize(self, size):
        return RES_ICONS.getBonusIcon(size, '{}_{}'.format(self.getName(), self.getValue()))

    def getIconLabel(self):
        pass


class MetaBonus(SimpleBonus):

    def isShowInGUI(self):
        return False

    def formatValue(self):
        return getLocalizedData({'value': self._value}, 'value')


class TokensBonus(SimpleBonus):
    _TOKEN_RECORD = namedtuple('_TOKEN_RECORD', ['id',
     'expires',
     'count',
     'limit'])

    def isShowInGUI(self):
        return False

    def formatValue(self):
        return None

    def getTokens(self):
        result = {}
        for tID, d in self._value.iteritems():
            expires = d.get('expires', {'at': None}) or {'at': None}
            result[tID] = self._TOKEN_RECORD(tID, expires.values()[0], d.get('count', 0), d.get('limit'))

        return result

    def getCount(self):
        return sum((v.get('count', 0) for v in self._value.values()))


class BattleTokensBonus(TokensBonus):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, name, value, isCompensation=False, ctx=None):
        super(TokensBonus, self).__init__(name, value, isCompensation, ctx)
        self._name = 'battleToken'

    def isShowInGUI(self):
        return True

    def formatValue(self):
        result = []
        for tokenID, _ in self._value.iteritems():
            complexToken = parseComplexToken(tokenID)
            if complexToken.isDisplayable:
                userName = self._getUserName(complexToken.styleID)
                result.append(i18n.makeString(TOOLTIPS.MISSIONS_TOKEN_HEADER, name=userName))

        return ', '.join(result) if result else None

    def getWrappedEpicBonusList(self):
        result = []
        for tokenID, value in self._value.iteritems():
            if tokenID == 'prestige_point':
                result.append({'id': 0,
                 'value': value.get('count', 1),
                 'icon': {AWARDS_SIZES.SMALL: RES_ICONS.getEpicBattlesPrestigePoints('48x48'),
                          AWARDS_SIZES.BIG: RES_ICONS.getEpicBattlesPrestigePoints('80x80')},
                 'type': 'custom/{}'.format(tokenID)})

        return result

    def _getUserName(self, styleID):
        webCache = self.eventsCache.prefetcher
        return i18n.makeString(webCache.getTokenInfo(styleID))


class LootBoxTokensBonus(TokensBonus):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, value, isCompensation=False, ctx=None):
        super(TokensBonus, self).__init__('battleToken', value, isCompensation, ctx)

    def isShowInGUI(self):
        return True

    def format(self):
        return ', '.join(self.formattedList())

    def formattedList(self):
        result = []
        for tokenID, tokenVal in self._value.iteritems():
            lootBox = self.itemsCache.items.tokens.getLootBoxByTokenID(tokenID)
            if lootBox is not None:
                result.append(makeHtmlString('html_templates:lobby/quests/bonuses', 'lootBox', {'lootBoxType': lootBox.getType(),
                 'value': tokenVal['count']}))

        return result


class TmanTemplateTokensBonus(TokensBonus):

    def __init__(self, value, isCompensation=False, ctx=None):
        super(TokensBonus, self).__init__('tmanToken', value, isCompensation, ctx)

    def isShowInGUI(self):
        return True


def personalMissionsTokensFactory(name, value, isCompensation=False, ctx=None):
    from gui.server_events.finders import PERSONAL_MISSION_TOKEN
    completionTokenID = PERSONAL_MISSION_TOKEN % (ctx['campaignID'], ctx['operationID'])
    result = []
    for tID, tValue in value.iteritems():
        if tID in PM_BRANCH_TO_FREE_TOKEN_NAME.values():
            result.append(FreeTokensBonus({tID: tValue}, isCompensation, ctx))
        if tID == completionTokenID:
            result.append(CompletionTokensBonus({tID: tValue}, isCompensation, ctx))
        result.append(TokensBonus(name, {tID: tValue}, isCompensation, ctx))

    return result


def tokensFactory(name, value, isCompensation=False, ctx=None):
    result = []
    for tID, tValue in value.iteritems():
        if tID.startswith(LOOTBOX_TOKEN_PREFIX):
            result.append(LootBoxTokensBonus({tID: tValue}, isCompensation, ctx))
        if tID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
            result.append(TmanTemplateTokensBonus({tID: tValue}, isCompensation, ctx))
        result.append(BattleTokensBonus(name, {tID: tValue}, isCompensation, ctx))

    return result


class FreeTokensBonus(TokensBonus):

    def __init__(self, value, isCompensation=False, ctx=None, hasPawned=False):
        super(FreeTokensBonus, self).__init__('freeTokens', value, isCompensation, ctx)
        self.__hasPawnedTokens = hasPawned

    def isShowInGUI(self):
        return self.getCount() > 0

    def formatValue(self):
        return str(self.getCount())

    def format(self):
        return makeHtmlString('html_templates:lobby/quests/bonuses', self._name, {'value': self.formatValue()})

    def areTokensPawned(self):
        return self.__hasPawnedTokens

    def getImageFileName(self):
        return '_'.join((self.getName(), str(self.__determineBranchID())))

    def __determineBranchID(self):
        result = PM_BRANCH.REGULAR
        for branch, token in PM_BRANCH_TO_FREE_TOKEN_NAME.iteritems():
            if token in self._value:
                result = branch

        return result


class CompletionTokensBonus(TokensBonus):

    def __init__(self, value, isCompensation=False, ctx=None):
        super(CompletionTokensBonus, self).__init__('completionTokens', value, isCompensation, ctx)

    def isShowInGUI(self):
        return self.getCount() > 0

    def formatValue(self):
        return str(self.getCount())

    def format(self):
        return makeHtmlString('html_templates:lobby/quests/bonuses', self._name, {'value': self.formatValue()})


class ItemsBonus(SimpleBonus):

    def getItems(self):
        if self._value is not None:
            _getItem = self.itemsCache.items.getItemByCD
            return dict(((_getItem(intCD), count) for intCD, count in self._value.iteritems()))
        else:
            return {}

    def format(self):
        result = []
        for item, count in self.getItems().iteritems():
            if item is not None and count:
                result.append(i18n.makeString('#quests:bonuses/items/name', name=item.userName, count=count))

        return ', '.join(result) if result else None

    def getList(self):
        result = []
        for item, count in self.getItems().iteritems():
            if item is not None and count:
                description = item.fullDescription
                if item.itemTypeID in (GUI_ITEM_TYPE.OPTIONALDEVICE, GUI_ITEM_TYPE.EQUIPMENT):
                    description = stripColorTagDescrTags(description)
                tooltip = makeTooltip(header=item.userName, body=description)
                result.append({'value': BigWorld.wg_getIntegralFormat(count),
                 'itemSource': item.icon,
                 'tooltip': tooltip})

        return result

    def getWrappedEpicBonusList(self):
        result = []
        for item, count in self.getItems().iteritems():
            if item is not None and count:
                result.append({'id': item.intCD,
                 'type': 'item/{}'.format(item.itemTypeName),
                 'value': count,
                 'icon': {AWARDS_SIZES.SMALL: item.getBonusIcon(AWARDS_SIZES.SMALL),
                          AWARDS_SIZES.BIG: item.getBonusIcon(AWARDS_SIZES.BIG)}})

        return result

    def hasIconFormat(self):
        return True

    def __getCommonAwardsVOs(self, item, count, iconSize='small', align=TEXT_ALIGN.RIGHT, withCounts=False):
        itemInfo = {'imgSource': item.getBonusIcon(iconSize),
         'label': text_styles.stats('x{}'.format(count)),
         'tooltip': self.makeItemTooltip(item),
         'align': align}
        if withCounts:
            itemInfo['count'] = count
        return itemInfo

    def getRankedAwardVOs(self, iconSize='small', withCounts=False, withKey=False):
        result = []
        for item, count in self.getItems().iteritems():
            itemInfo = self.__getCommonAwardsVOs(item, count, iconSize=iconSize, withCounts=withCounts)
            if item.itemTypeName == 'optionalDevice':
                if item.isDeluxe():
                    itemInfo['highlightType'] = SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT
                    itemInfo['overlayType'] = SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS
            if withKey:
                itemInfo['itemKey'] = 'item_{}'.format(item.intCD)
            result.append(itemInfo)

        return result

    def getEpicAwardVOs(self, withDescription=False, iconSize='big', withCounts=False):
        result = []
        for item, count in self.getItems().iteritems():
            itemInfo = self.__getCommonAwardsVOs(item, count, iconSize, align=TEXT_ALIGN.CENTER, withCounts=withCounts)
            itemInfo.update(_EPIC_AWARD_STATIC_VO_ENTRIES)
            result.append(itemInfo)

        return result

    @staticmethod
    def makeItemTooltip(item):
        description = item.fullDescription
        if item.itemTypeID in (GUI_ITEM_TYPE.OPTIONALDEVICE, GUI_ITEM_TYPE.EQUIPMENT):
            description = stripColorTagDescrTags(description)
        return makeTooltip(header=item.userName, body=description)


class GoodiesBonus(SimpleBonus):
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def getBoosters(self):
        return self._getGoodies(self.goodiesCache.getBooster)

    def getDiscounts(self):
        return self._getGoodies(self.goodiesCache.getDiscount)

    def _getGoodies(self, goodieGetter):
        goodies = {}
        if self._value is not None:
            for boosterID, info in self._value.iteritems():
                goodie = goodieGetter(int(boosterID))
                if goodie is not None and goodie.enabled:
                    goodies[goodie] = info.get('count', 1)

        return goodies

    def format(self):
        return ', '.join(self.formattedList())

    @staticmethod
    def __makeBoosterVO(booster):
        return {'icon': booster.icon,
         'showCount': False,
         'qualityIconSrc': booster.getQualityIcon(),
         'slotLinkage': BOOSTER_CONSTANTS.SLOT_UI,
         'showLeftTime': False,
         'boosterId': booster.boosterID}

    def hasIconFormat(self):
        return True

    def getList(self):
        result = []
        for booster, count in sorted(self.getBoosters().iteritems(), key=lambda (booster, count): booster.boosterType):
            if booster is not None:
                result.append({'value': BigWorld.wg_getIntegralFormat(count),
                 'tooltip': TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO,
                 'boosterVO': self.__makeBoosterVO(booster)})

        for discount, count in sorted(self.getDiscounts().iteritems()):
            if discount is not None:
                tooltip = makeTooltip(header=discount.userName, body=discount.description)
                result.append({'value': discount.getFormattedValue(),
                 'itemSource': discount.icon,
                 'tooltip': tooltip})

        return result

    def getWrappedEpicBonusList(self):
        result = []
        for booster, count in self.getBoosters().iteritems():
            if booster is not None:
                result.append({'id': booster.boosterID,
                 'type': 'goodie/{}'.format(booster.getTypeAsString()),
                 'value': count,
                 'icon': {AWARDS_SIZES.SMALL: booster.icon,
                          AWARDS_SIZES.BIG: booster.bigIcon}})

        for discount, count in self.getDiscounts().iteritems():
            if discount is not None:
                result.append({'id': discount.discountID,
                 'type': 'discount/{}'.format(discount.targetType),
                 'value': discount.getFormattedValue(),
                 'icon': {AWARDS_SIZES.SMALL: discount.icon,
                          AWARDS_SIZES.BIG: discount.bigIcon}})

        return result

    def formattedList(self):
        result = []
        for booster, count in self.getBoosters().iteritems():
            if booster is not None:
                result.append(i18n.makeString('#quests:bonuses/boosters/name', name=booster.userName, quality=booster.qualityStr, count=count))

        for discount, count in self.getDiscounts().iteritems():
            if discount is not None:
                result.append(i18n.makeString('#quests:bonuses/discount/name', name=discount.userName, targetName=discount.targetName, effectValue=discount.getFormattedValue(), count=count))

        return result

    def __getCommonAwardsVOs(self, item, count, iconSize='small', align=TEXT_ALIGN.RIGHT, withCounts=False):
        itemData = {'imgSource': RES_ICONS.getBonusIcon(iconSize, item.boosterGuiType),
         'label': text_styles.hightlight('x{}'.format(count)),
         'align': align}
        itemData.update(self.__itemTooltip(item))
        if withCounts:
            itemData['count'] = count
        return itemData

    def getRankedAwardVOs(self, iconSize='small', withCounts=False, withKey=False):
        result = []
        for booster, count in self.getBoosters().iteritems():
            if booster is not None:
                itemData = self.__getCommonAwardsVOs(booster, count, iconSize=iconSize, withCounts=withCounts)
                if withKey:
                    itemData['itemKey'] = 'booster_{}'.format(booster.boosterID)
                result.append(itemData)

        return result

    def getEpicAwardVOs(self, withDescription=False, iconSize='big', withCounts=False):
        result = []
        for booster, count in self.getBoosters().iteritems():
            if booster is not None:
                itemData = self.__getCommonAwardsVOs(booster, count, iconSize, align=TEXT_ALIGN.CENTER, withCounts=withCounts)
                itemData.update(_EPIC_AWARD_STATIC_VO_ENTRIES)
                result.append(itemData)

        return result

    @staticmethod
    def __itemTooltip(booster):
        return {'isSpecial': True,
         'specialAlias': TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO,
         'specialArgs': [booster.boosterID]}


class VehiclesBonus(SimpleBonus):

    @classmethod
    def isNonZeroCompensation(cls, vehInfo):
        compensatedNumber = vehInfo.get('compensatedNumber', 0)
        compensation = vehInfo.get('customCompensation')
        if compensatedNumber and compensation is not None:
            money = Money(*compensation)
            if money == _ZERO_COMPENSATION_MONEY:
                return False
        return True

    def formatValue(self):
        result = []
        for item, _ in self.getVehicles():
            result.append(item.shortUserName)

        return ', '.join(result)

    def format(self):
        return ', '.join(self.formattedList())

    def formattedList(self):
        result = []
        for item, vehInfo in self.getVehicles():
            tmanRoleLevel = self.getTmanRoleLevel(vehInfo)
            rentDays = self.getRentDays(vehInfo)
            vInfoLabels = []
            if rentDays is not None:
                rentDaysStr = makeHtmlString('html_templates:lobby/quests/bonuses', 'rentDays', {'value': str(rentDays)})
                vInfoLabels.append(rentDaysStr)
            if tmanRoleLevel is not None:
                crewLvl = i18n.makeString('#quests:bonuses/vehicles/crewLvl', tmanRoleLevel)
                vInfoLabels.append(crewLvl)
            if vInfoLabels:
                result.append(text_styles.standard(i18n.makeString('#quests:bonuses/vehicles/name', name=text_styles.main(item.userName), vehInfo='; '.join(vInfoLabels))))
            result.append(text_styles.main(item.userName))

        return result

    def getWrappedEpicBonusList(self):
        result = []
        for item, _ in self.getVehicles():
            result.append({'id': item.intCD,
             'type': 'vehicle/{}'.format(item.type),
             'value': 1,
             'icon': {AWARDS_SIZES.SMALL: item.iconSmall,
                      AWARDS_SIZES.BIG: item.icon}})

        return result

    def getIcon(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_TANK

    def getTooltipIcon(self):
        vehicle, _ = self.getVehicles()[0]
        return vehicle.icon

    def getVehicles(self):
        result = []
        if self._value is not None:
            if isinstance(self._value, dict):
                for intCD, vehInfo in self._value.iteritems():
                    item = self.itemsCache.items.getItemByCD(intCD)
                    if item is not None:
                        result.append((item, vehInfo))

            elif isinstance(self._value, list):
                for subDict in self._value:
                    for intCD, vehInfo in subDict.iteritems():
                        item = self.itemsCache.items.getItemByCD(intCD)
                        if item is not None:
                            result.append((item, vehInfo))

        return result

    def isRentVehicle(self, vehInfo):
        return True if self.getRentBattles(vehInfo) or self.getRentDays(vehInfo) or self.getRentWins(vehInfo) else False

    def compensation(self, vehicle, bonus):
        bonuses = []
        for curVehicle, vehInfo in self.getVehicles():
            compensatedNumber = vehInfo.get('compensatedNumber', 0)
            compensation = vehInfo.get('customCompensation')
            if compensatedNumber and compensation is not None and curVehicle == vehicle:
                money = Money(*compensation)
                while compensatedNumber > 0:
                    for currency, value in money.iteritems():
                        if value:
                            cls = _BONUSES.get(currency)
                            bonuses.append(cls(currency, value, isCompensation=True, compensationReason=bonus))

                    compensatedNumber -= 1

        return bonuses

    def checkIsCompensatedVehicle(self, vehicle):
        for curVehicle, vehInfo in self.getVehicles():
            compensation = vehInfo.get('customCompensation')
            return curVehicle == vehicle and compensation

        return False

    def getIconLabel(self):
        pass

    def __getCommonAwardsVOs(self, vehicle, vehInfo, iconSize='small', align=TEXT_ALIGN.RIGHT, withCounts=False):
        vehicleVO = self.__getVehicleVO(vehicle, vehInfo, partial(RES_ICONS.getBonusIcon, iconSize))
        vehicleVO.update({'label': self.getIconLabel()})
        vehicleVO['align'] = align
        if withCounts:
            vehicleVO['count'] = 1
        return vehicleVO

    def getRankedAwardVOs(self, iconSize='small', withCounts=False, withKey=False):
        result = []
        for vehicle, vehInfo in self.getVehicles():
            vehicleVO = self.__getCommonAwardsVOs(vehicle, vehInfo, iconSize=iconSize, withCounts=withCounts)
            if withKey:
                vehicleVO['itemKey'] = 'vehicle_{}'.format(vehicle.intCD)
            result.append(vehicleVO)

        return result

    def getEpicAwardVOs(self, withDescription=False, iconSize='big', withCounts=False):
        result = []
        for vehicle, vehInfo in self.getVehicles():
            vehicleVO = self.__getCommonAwardsVOs(vehicle, vehInfo, iconSize, align=TEXT_ALIGN.CENTER, withCounts=withCounts)
            vehicleVO.update(_EPIC_AWARD_STATIC_VO_ENTRIES)
            if withDescription:
                vehicleVO['title'] = i18n.makeString(TOOLTIPS.getAwardHeader(self._name))
                vehicleVO['description'] = i18n.makeString(TOOLTIPS.getAwardBody(self._name))
            result.append(vehicleVO)

        return result

    @classmethod
    def getTmanRoleLevel(cls, vehInfo):
        if 'noCrew' not in vehInfo:
            if 'crewLvl' in vehInfo:
                return calculateRoleLevel(vehInfo.get('crewLvl', DEFAULT_CREW_LVL), vehInfo.get('crewFreeXP', 0))
            if 'tankmen' in vehInfo:
                for tman in vehInfo['tankmen']:
                    if isinstance(tman, str):
                        tankmanDecsr = tankmen.TankmanDescr(compactDescr=tman)
                        if tankmanDecsr.role == Tankman.ROLES.COMMANDER:
                            return calculateRoleLevel(tankmanDecsr.roleLevel, tankmanDecsr.freeXP)
                    if tman['role'] == Tankman.ROLES.COMMANDER:
                        return calculateRoleLevel(tman.get('roleLevel', DEFAULT_CREW_LVL), tman.get('freeXP', 0))

        return None

    @staticmethod
    def getRentDays(vehInfo):
        if 'rent' not in vehInfo:
            return None
        else:
            time = vehInfo.get('rent', {}).get('time')
            if time:
                if time == float('inf'):
                    return None
                if time <= time_utils.DAYS_IN_YEAR:
                    return int(time)
                return None
            return None

    @staticmethod
    def getRentBattles(vehInfo):
        return vehInfo.get('rent', {}).get('battles')

    @staticmethod
    def getRentWins(vehInfo):
        return vehInfo.get('rent', {}).get('wins')

    @staticmethod
    def getRentSeason(vehInfo):
        return vehInfo.get('rent', {}).get('season')

    def __getVehicleVO(self, vehicle, vehicleInfo, iconGetter):
        tmanRoleLevel = self.getTmanRoleLevel(vehicleInfo)
        rentDays = self.getRentDays(vehicleInfo)
        if rentDays:
            iconName = 'vehicles_rent'
            rentExpiryTime = time_utils.getCurrentTimestamp() + rentDays * time_utils.ONE_DAY
        else:
            iconName = 'vehicles'
            rentExpiryTime = 0
        return {'imgSource': iconGetter(iconName),
         'isSpecial': True,
         'specialAlias': TOOLTIPS_CONSTANTS.AWARD_VEHICLE,
         'specialArgs': [vehicle.intCD, tmanRoleLevel, rentExpiryTime]}


class BadgesGroupBonus(SimpleBonus):

    def getBadges(self):
        groupID = self._value
        badges = self.itemsCache.items.getBadges()
        return [ badge for badge in badges.itervalues() if groupID == badge.group ]


class DossierBonus(SimpleBonus):

    def getRecords(self):
        records = {}
        if self._value is not None:
            for dossierType in self._value:
                if dossierType != DOSSIER_TYPE.CLAN:
                    for name, data in self._value[dossierType].iteritems():
                        records[name] = data.get('value', 0)

        return records

    def getAchievements(self):
        return self.__getItems(_isAchievement)

    def getBadges(self):
        result = []
        badges = None
        for (block, record), _ in self.getRecords().iteritems():
            if _isBadge(block):
                badgeID = int(record)
                if badges is None:
                    badges = self.itemsCache.items.getBadges()
                if badgeID in badges:
                    result.append(badges[badgeID])

        return result

    def format(self):
        return ', '.join(self.formattedList())

    def formattedList(self):
        return self.getAchievements()

    def getWrappedEpicBonusList(self):
        result = []
        for block, record in self.getRecords().iterkeys():
            if block == 'singleAchievements':
                blockID = RECORD_DB_IDS[block, record]
            else:
                blockID = record
            result.append({'id': blockID,
             'type': block,
             'value': 1,
             'icon': self.__getEpicBonusImages(block, record)})

        return result

    def __getEpicBonusImages(self, block, record):
        if block == 'playerBadges':
            return {AWARDS_SIZES.SMALL: getBadgeIconPath(BADGES_ICONS.X48, record),
             AWARDS_SIZES.BIG: getBadgeIconPath(BADGES_ICONS.X80, record)}
        return {AWARDS_SIZES.SMALL: RES_ICONS.getEpicAchievementIcon(ICONS_SIZES.X48, record),
         AWARDS_SIZES.BIG: RES_ICONS.getEpicAchievementIcon(ICONS_SIZES.X80, record)} if block == 'singleAchievements' else {}

    def __getCommonAwardsVOs(self, block, record, iconSize='small', withCounts=False):
        badgesIconSizes = {'big': BADGES_ICONS.X80,
         'small': BADGES_ICONS.X48}
        if _isBadge(block):
            header = i18n.makeString(BADGE.badgeName(record))
            body = i18n.makeString(BADGE.badgeDescriptor(record))
            note = i18n.makeString(BADGE.BADGE_NOTE)
            badgeVO = {'imgSource': getBadgeIconPath(badgesIconSizes[iconSize], record),
             'label': '',
             'tooltip': makeTooltip(header, body, note)}
            if withCounts:
                badgeVO['count'] = 1
            return badgeVO
        else:
            return None

    def getRankedAwardVOs(self, iconSize='small', withCounts=False, withKey=False):
        result = []
        for (block, record), _ in self.getRecords().iteritems():
            badgeVO = self.__getCommonAwardsVOs(block, record, iconSize=iconSize, withCounts=withCounts)
            if not badgeVO:
                continue
            if withKey:
                badgeVO['itemKey'] = BADGE.badgeName(record)
            result.append(badgeVO)

        return result

    def getEpicAwardVOs(self, withDescription=False, iconSize='big', withCounts=False):
        result = []
        for (block, record), _ in self.getRecords().iteritems():
            badgeVO = self.__getCommonAwardsVOs(block, record, iconSize, withCounts=withCounts)
            if not badgeVO:
                continue
            badgeVO['align'] = TEXT_ALIGN.CENTER
            badgeVO.update(_EPIC_AWARD_STATIC_VO_ENTRIES)
            if withDescription:
                badgeVO['title'] = i18n.makeString(BADGE.badgeName(record))
                badgeVO['description'] = i18n.makeString(BADGE.badgeDescriptor(record))
            result.append(badgeVO)

        return result

    def __getItems(self, filterFunc):
        result = []
        for (block, record), value in self.getRecords().iteritems():
            if filterFunc(block):
                achieve = _getAchievement(block, record, value)
                if achieve is not None:
                    result.append(achieve)

        return result


class PersonalMissionDossierBonus(DossierBonus):

    def isShowInGUI(self):
        return bool(self.getBadges())


class TankmenBonus(SimpleBonus):
    _TankmanInfoRecord = namedtuple('_TankmanInfoRecord', ['nationID',
     'role',
     'vehicleTypeID',
     'firstNameID',
     'fnGroupID',
     'lastNameID',
     'lnGroupID',
     'iconID',
     'iGroupID',
     'isPremium',
     'roleLevel',
     'freeXP',
     'skills',
     'isFemale',
     'freeSkills'])

    def formatValue(self):
        result = []
        for group in self.getTankmenGroups().itervalues():
            if group['skills']:
                labelI18nKey = '#quests:bonuses/item/tankmen/with_skills'
            else:
                labelI18nKey = '#quests:bonuses/item/tankmen/no_skills'
            result.append(i18n.makeString(labelI18nKey, **group))

        return ' '.join(result)

    def getTankmenData(self):
        result = []
        if self._value is not None:
            for tankmanData in self._value:
                if isinstance(tankmanData, str):
                    result.append(self._makeTmanInfoByDescr(tankmen.TankmanDescr(compactDescr=tankmanData)))
                result.append(makeTupleByDict(self._TankmanInfoRecord, tankmanData))

        return result

    def getTankmenGroups(self):
        groups = {}
        for tmanInfo in self.getTankmenData():
            roleLevel = calculateRoleLevel(tmanInfo.roleLevel, tmanInfo.freeXP, typeID=(tmanInfo.nationID, tmanInfo.vehicleTypeID))
            if tmanInfo.vehicleTypeID not in groups:
                vehIntCD = vehicles.makeIntCompactDescrByID('vehicle', tmanInfo.nationID, tmanInfo.vehicleTypeID)
                groups[tmanInfo.vehicleTypeID] = {'vehName': self.itemsCache.items.getItemByCD(vehIntCD).shortUserName,
                 'skills': len(tmanInfo.skills),
                 'roleLevel': roleLevel}
            group = groups[tmanInfo.vehicleTypeID]
            group['skills'] += len(tmanInfo.skills)
            group['roleLevel'] = min(group['roleLevel'], roleLevel)

        return groups

    def getIcon(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_TANKMAN

    def getTooltipIcon(self):
        for tmanInfo in self.getTankmenData():
            if tmanInfo.isFemale:
                return RES_ICONS.MAPS_ICONS_QUESTS_TANKMANFEMALEGRAY

        return RES_ICONS.MAPS_ICONS_REFERRAL_REFSYS_MEN_BW

    def getCount(self):
        return len(self._value) if self._value is not None else 0

    @classmethod
    def _makeTmanInfoByDescr(cls, td):
        return cls._TankmanInfoRecord(td.nationID, td.role, td.vehicleTypeID, td.firstNameID, -1, td.lastNameID, -1, td.iconID, -1, td.isPremium, td.roleLevel, td.freeXP, td.skills, td.isFemale, [])


class TankwomanBonus(TankmenBonus):

    def __init__(self, name, value, isCompensation=False, ctx=None):
        super(TankwomanBonus, self).__init__(name, value, isCompensation)
        self._name = 'tankwomanBonus'

    def formatValue(self):
        result = []
        for tmanInfo in self.getTankmenData():
            if tmanInfo.isFemale:
                result.append(i18n.makeString(QUESTS.BONUSES_ITEM_TANKWOMAN))
            result.append(i18n.makeString(QUESTS.BONUSES_TANKMEN_DESCRIPTION, value=getRoleUserName(tmanInfo.role)))

        return ', '.join(result)


class CustomizationsBonus(SimpleBonus):
    c11n = dependency.descriptor(ICustomizationService)
    INFOTIP_ARGS_ORDER = ('intCD', 'showPrice')

    def getList(self):
        result = []
        separator = ''
        customizations = self.getCustomizations()
        customizationsCountMax = len(customizations) - 1
        if customizationsCountMax > 0:
            separator = ', '
        for count, itemData in enumerate(customizations):
            boundVehicle = itemData.get('vehTypeCompDescr')
            boundToCurrentVehicle = itemData.get('boundToCurrentVehicle', False)
            item = self.getC11nItem(itemData)
            value = itemData.get('value', 0)
            valueStr = None
            if value > 1:
                valueStr = text_styles.main(i18n.makeString(QUESTS.BONUSES_CUSTOMIZATION_VALUE, count=value))
            key = VEHICLE_CUSTOMIZATION.getElementBonusDesc(item.itemTypeName)
            bonusDesc = ''
            if key is not None:
                bonusDesc = _ms(key, value=item.userName)
                if value > 0:
                    bonusDesc = bonusDesc + _ms(VEHICLE_CUSTOMIZATION.ELEMENTBONUS_FACTOR, count=value)
                if count < customizationsCountMax:
                    bonusDesc = bonusDesc + separator
            result.append({'intCD': item.intCD,
             'texture': item.icon,
             'value': value,
             'valueStr': valueStr,
             'boundVehicle': boundVehicle,
             'boundToCurrentVehicle': boundToCurrentVehicle,
             'showPrice': False,
             'description': bonusDesc})

        return result

    def getWrappedEpicBonusList(self):
        result = []
        for itemData in self.getCustomizations():
            itemType = itemData.get('custType')
            itemTypeID = GUI_ITEM_TYPE_INDICES.get(itemType)
            item = self.c11n.getItemByID(itemTypeID, itemData.get('id'))
            smallIcon = item.getBonusIcon(AWARDS_SIZES.SMALL)
            bigIcon = item.getBonusIcon(AWARDS_SIZES.BIG)
            typeStr = itemType
            if itemType == 'decal':
                typeStr = 'decal/1'
            elif itemType == 'paint':
                typeStr = 'paint/all'
            elif itemType == 'camouflage':
                typeStr = 'camouflage/all'
            elif itemType == 'style':
                smallIcon = RES_ICONS.getBonusIcon(AWARDS_SIZES.SMALL, itemType)
                bigIcon = RES_ICONS.getBonusIcon(AWARDS_SIZES.BIG, itemType)
            result.append({'id': itemData.get('id'),
             'type': typeStr,
             'value': itemData.get('value', 0),
             'icon': {AWARDS_SIZES.SMALL: smallIcon,
                      AWARDS_SIZES.BIG: bigIcon}})

        return result

    def getCustomizations(self):
        return self._value or []

    def compensation(self):
        bonuses = []
        substitutes = []
        cache = vehicles.g_cache.customization20()
        for customizationItem in self._value:
            c11nItem = self.getC11nItem(customizationItem)
            itemType, itemId = cc.splitIntDescr(c11nItem.intCD)
            c11nComponent = cache.itemTypes[itemType][itemId]
            count = customizationItem.get('value')
            inventoryCount = c11nItem.inventoryCount
            maxNumber = c11nComponent.maxNumber
            compensationCount = count - max(0, maxNumber - inventoryCount)
            if compensationCount > 0 and maxNumber != 0:
                realCount = count - compensationCount
                if realCount > 0:
                    substituteItem = copy.deepcopy(customizationItem)
                    substituteItem['value'] = realCount
                    substitutes.append(substituteItem)
                compensation = customizationItem.get('customCompensation')
                money = Money.makeMoney(compensation)
                if money is not None:
                    for currency, value in money.iteritems():
                        if value:
                            cls = _BONUSES.get(currency)
                            bonuses.append(cls(currency, value * compensationCount, isCompensation=True))

            substitutes.append(copy.deepcopy(customizationItem))

        bonuses.insert(0, CustomizationsBonus('customizations', substitutes))
        return bonuses

    def getC11nItem(self, item):
        itemTypeName = item.get('custType')
        itemID = item.get('id')
        if itemTypeName == 'projection_decal':
            itemTypeID = GUI_ITEM_TYPE.PROJECTION_DECAL
        elif itemTypeName == 'personal_number':
            itemTypeID = GUI_ITEM_TYPE.PERSONAL_NUMBER
        else:
            itemTypeID = GUI_ITEM_TYPE_INDICES.get(itemTypeName)
        c11nItem = self.c11n.getItemByID(itemTypeID, itemID)
        return c11nItem

    def __getCommonAwardsVOs(self, item, data, iconSize='small', align=TEXT_ALIGN.RIGHT, withCounts=False):
        c11nItem = self.getC11nItem(item)
        count = item.get('value', 1)
        itemData = {'imgSource': RES_ICONS.getBonusIcon(iconSize, c11nItem.itemTypeName),
         'label': text_styles.hightlight('x{}'.format(count)),
         'align': align}
        itemData.update(self.__itemTooltip(data))
        if withCounts:
            itemData['count'] = count
        return itemData

    def getRankedAwardVOs(self, iconSize='small', withCounts=False, withKey=False):
        result = []
        for item, data in zip(self.getCustomizations(), self.getList()):
            itemData = self.__getCommonAwardsVOs(item, data, iconSize=iconSize, withCounts=withCounts)
            if withKey:
                itemData['itemKey'] = 'customization_{}'.format(item.get('custType'))
            result.append(itemData)

        return result

    def getEpicAwardVOs(self, withDescription=False, iconSize='big', withCounts=False):
        result = []
        for item, data in zip(self.getCustomizations(), self.getList()):
            itemData = self.__getCommonAwardsVOs(item, data, iconSize, align=TEXT_ALIGN.CENTER, withCounts=withCounts)
            itemData.update(_EPIC_AWARD_STATIC_VO_ENTRIES)
            if withDescription:
                c11nItem = self.getC11nItem(item)
                itemData['description'] = c11nItem.userType
                itemData['title'] = c11nItem.userName
            result.append(itemData)

        return result

    def __itemTooltip(self, data):
        return {'isSpecial': True,
         'specialAlias': TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM,
         'specialArgs': [ data[o] for o in self.INFOTIP_ARGS_ORDER ]}


class BoxBonus(SimpleBonus):
    __rankedIconSizes = {'big': '100x88',
     'small': '48x48'}

    class HANDLER_NAMES(object):
        RANKED = 'ranked'

    def __init__(self, name, value, isCompensation=False, ctx=None):
        super(BoxBonus, self).__init__(name, value, isCompensation)
        self.__iconsHandlerData = ('', None)
        self.__tooltipType = None
        self.__iconHandlers = {self.HANDLER_NAMES.RANKED: self.__rankedIconHandler}
        return

    def setupIconHandler(self, handlerData, handlerParams):
        self.__iconsHandlerData = (handlerData, handlerParams)

    def setTooltipType(self, tooltipType):
        self.__tooltipType = tooltipType

    def getIconBySize(self, size):
        handlerName, params = self.__iconsHandlerData
        handler = self.__iconHandlers.get(handlerName)
        return handler(params, size) if handler else None

    def getIconLabel(self):
        pass

    def getTooltip(self):
        name = self._name
        if self.__tooltipType is not None:
            name = '/'.join([name, self.__tooltipType])
        return _getItemTooltip(name)

    def __rankedIconHandler(self, params, sizeLabel):
        boxType, number = params
        size = self.__rankedIconSizes[sizeLabel]
        return RES_ICONS.getRankedBoxIcon(size, boxType, '', number)


def blueprintBonusFactory(name, value, isCompensation=False, ctx=None):
    blueprintBonuses = []
    for fragmentCD, fragmentCount in value.iteritems():
        fragmentType = getFragmentType(fragmentCD)
        if fragmentType == BlueprintTypes.VEHICLE:
            blueprintBonuses.append(VehicleBlueprintBonus(name, (fragmentCD, fragmentCount), isCompensation, ctx))
        if fragmentType == BlueprintTypes.INTELLIGENCE_DATA:
            vehicleCD = getVehicleCDForIntelligence(fragmentCD)
            blueprintBonuses.append(IntelligenceBlueprintBonus(name, (vehicleCD, fragmentCount), isCompensation, ctx))
        if fragmentType == BlueprintTypes.NATIONAL:
            vehicleCD = getVehicleCDForNational(fragmentCD)
            blueprintBonuses.append(NationalBlueprintBonus(name, (vehicleCD, fragmentCount), isCompensation, ctx))

    return blueprintBonuses


def crewSkinsBonusFactory(name, value, isCompensation=False, ctx=None):
    bonuses = []
    for crewSkinData in value:
        bonuses.append(CrewSkinsBonus(name=name, value=crewSkinData, isCompensation=isCompensation, ctx=ctx))

    return bonuses


class BlueprintsBonusSubtypes(CONST_CONTAINER):
    FINAL_FRAGMENT = 'BlueprintFinalFragmentCongrats'
    UNIVERSAL_FRAGMENT = 'BlueprintUniversalFragmentCongrats'
    NATION_FRAGMENT = 'BlueprintNationFragmentCongrats'
    VEHICLE_FRAGMENT = 'BlueprintVehicleFragmentCongrats'
    USE_CONGRATS = (FINAL_FRAGMENT, VEHICLE_FRAGMENT)


class VehicleBlueprintBonus(SimpleBonus):

    def getBlueprintName(self):
        return BlueprintsBonusSubtypes.FINAL_FRAGMENT if self.__isFinalFragment() else BlueprintsBonusSubtypes.VEHICLE_FRAGMENT

    def getBlueprintSpecialAlias(self):
        return TOOLTIPS_CONSTANTS.BLUEPRINT_INFO if self.__isFinalFragment() else TOOLTIPS_CONSTANTS.BLUEPRINT_FRAGMENT_INFO

    def getBlueprintSpecialArgs(self):
        return self._getFragmentCD()

    def formatBlueprintValue(self):
        return text_styles.neutral(self.itemsCache.items.getItemByCD(self._getFragmentCD()).shortUserName)

    def getImage(self, size='big'):
        return RES_ICONS.getBlueprintFragment(size, 'vehicle_complete') if self.__isFinalFragment() else RES_ICONS.getBlueprintFragment(size, 'vehicle')

    def getCount(self):
        return self._value[1]

    def _getFragmentCD(self):
        return self._value[0]

    def __isFinalFragment(self):
        level = self.itemsCache.items.getItemByCD(self._getFragmentCD()).level
        filledCount, totalCount = self.itemsCache.items.blueprints.getBlueprintCount(self._getFragmentCD(), level)
        return True if filledCount == totalCount else False


class IntelligenceBlueprintBonus(VehicleBlueprintBonus):

    def getBlueprintName(self):
        return BlueprintsBonusSubtypes.UNIVERSAL_FRAGMENT

    def getBlueprintSpecialArgs(self):
        return int(makeIntelligenceCD(self._getFragmentCD()))

    def getImage(self, size='big'):
        return RES_ICONS.getBlueprintFragment(size, 'intelligence')

    def getBlueprintSpecialAlias(self):
        return TOOLTIPS_CONSTANTS.BLUEPRINT_FRAGMENT_INFO

    def formatBlueprintValue(self):
        pass


class NationalBlueprintBonus(VehicleBlueprintBonus):

    def getBlueprintName(self):
        return BlueprintsBonusSubtypes.NATION_FRAGMENT

    def getBlueprintSpecialArgs(self):
        return int(makeNationalCD(self._getFragmentCD()))

    def getImage(self, size='big'):
        nationID = getFragmentNationID(self._getFragmentCD())
        import nations
        return RES_ICONS.getBlueprintFragment(size, nations.NAMES[nationID])

    def getBlueprintSpecialAlias(self):
        return TOOLTIPS_CONSTANTS.BLUEPRINT_FRAGMENT_INFO

    def formatBlueprintValue(self):
        pass


class CrewSkinsBonus(SimpleBonus):

    def getItems(self):
        if self._value is None:
            return []
        else:
            getItem = self.itemsCache.items.getCrewSkin
            result = []
            crewSkinID = self._value.get('id', NO_CREW_SKIN_ID)
            count = self._value.get('count', 0)
            customCompensation = self._value.get('customCompensation', None)
            compensatedNumber = self._value.get('compensatedNumber', None)
            if crewSkinID != NO_CREW_SKIN_ID and (count > 0 or customCompensation is not None):
                crewSkinItem = getItem(crewSkinID)
                if crewSkinItem is not None:
                    if customCompensation is not None and compensatedNumber is not None:
                        customCompensation = (customCompensation,)
                    if compensatedNumber > 0:
                        result.append((crewSkinItem,
                         0,
                         customCompensation,
                         compensatedNumber))
                    if count > 0:
                        result.append((crewSkinItem,
                         count,
                         None,
                         0))
            return result

    def format(self):
        return ', '.join(self.formattedList())

    def formattedList(self):
        sortedByRarity = {}
        for item, count, _, _ in self.getItems():
            if count:
                rarity = item.getRarity()
                totalCount = sortedByRarity.setdefault(rarity, 0)
                sortedByRarity[rarity] = totalCount + count

        result = []
        for rarity, count in sortedByRarity.iteritems():
            result.append(makeHtmlString('html_templates:lobby/quests/bonuses', 'crewSkin', {'value': count,
             'rarity': str(rarity)}))

        return result

    def getWrappedEpicBonusList(self):
        result = []
        for item, count, _, _ in self.getItems():
            if item is not None:
                result.append({'id': item.intCD,
                 'type': 'item/{}'.format(item.itemTypeName),
                 'value': count,
                 'icon': {AWARDS_SIZES.SMALL: item.getBonusIcon(AWARDS_SIZES.SMALL),
                          AWARDS_SIZES.BIG: item.getBonusIcon(AWARDS_SIZES.BIG)}})

        return result

    def compensation(self, compensatedNumber, customCompensation, bonus):
        bonuses = []
        if compensatedNumber > 0 and customCompensation is not None:
            money = Money(*customCompensation)
            currencies = money.getSetCurrencies(byWeight=True)
            for currency in currencies:
                cls = _BONUSES.get(currency)
                bonuses.append(cls(currency, money.get(currency=currency), isCompensation=True, compensationReason=bonus))

        return bonuses

    def __getCommonAwardsVOs(self, item, count, iconSize='small', align=TEXT_ALIGN.RIGHT, withCounts=False):
        itemInfo = {'imgSource': item.getBonusIcon(iconSize),
         'label': text_styles.stats('x{}'.format(count)),
         'align': align,
         'isSpecial': True,
         'specialArgs': [item.id],
         'specialAlias': TOOLTIPS_CONSTANTS.CREW_SKIN}
        if withCounts:
            itemInfo['count'] = count
        return itemInfo


_BONUSES = {Currency.CREDITS: CreditsBonus,
 Currency.GOLD: GoldBonus,
 Currency.CRYSTAL: CrystalBonus,
 'strBonus': SimpleBonus,
 'xp': IntegralBonus,
 'freeXP': FreeXpBonus,
 'tankmenXP': IntegralBonus,
 'xpFactor': FloatBonus,
 'creditsFactor': FloatBonus,
 'freeXPFactor': FloatBonus,
 'tankmenXPFactor': FloatBonus,
 'dailyXPFactor': FloatBonus,
 'slots': CountableIntegralBonus,
 'berths': CountableIntegralBonus,
 'premium': PremiumDaysBonus,
 'vehicles': VehiclesBonus,
 'meta': MetaBonus,
 'tokens': {'default': tokensFactory,
            _ET.BATTLE_QUEST: tokensFactory,
            _ET.TOKEN_QUEST: tokensFactory,
            _ET.PERSONAL_QUEST: tokensFactory,
            _ET.PERSONAL_MISSION: personalMissionsTokensFactory,
            _ET.ELEN_QUEST: tokensFactory},
 'dossier': {'default': DossierBonus,
             _ET.PERSONAL_MISSION: PersonalMissionDossierBonus},
 'tankmen': {'default': TankmenBonus,
             _ET.PERSONAL_MISSION: TankwomanBonus},
 'customizations': CustomizationsBonus,
 'goodies': GoodiesBonus,
 'items': ItemsBonus,
 'oneof': BoxBonus,
 'badgesGroup': BadgesGroupBonus,
 'blueprints': blueprintBonusFactory,
 'crewSkins': crewSkinsBonusFactory}
_BONUSES_PRIORITY = ('tokens', 'oneof')
_BONUSES_ORDER = dict(((n, idx) for idx, n in enumerate(_BONUSES_PRIORITY)))

def compareBonuses(bonusName1, bonusName2):
    if bonusName1 not in _BONUSES_ORDER and bonusName2 not in _BONUSES_ORDER:
        return cmp(bonusName1, bonusName2)
    if bonusName1 not in _BONUSES_ORDER:
        return 1
    return -1 if bonusName2 not in _BONUSES_ORDER else _BONUSES_ORDER[bonusName1] - _BONUSES_ORDER[bonusName2]


def _getFromTree(tree, path):
    if not tree or not path:
        return
    else:
        key = path[0]
        subTree = None
        if key in tree:
            subTree = tree[key]
        elif 'default' in tree:
            subTree = tree['default']
        return _getFromTree(subTree, path[1:]) if isinstance(subTree, dict) else subTree


def _initFromTree(key, name, value, isCompensation=False, ctx=None):
    factory = _getFromTree(_BONUSES, key)
    if factory is not None:
        result = factory(name, value, isCompensation, ctx)
        if result is not None:
            if not isinstance(result, list):
                return [result]
            return result
    return []


def getBonuses(quest, name, value, isCompensation=False, ctx=None):
    questType = quest.getType()
    key = [name, questType]
    ctx = ctx or {}
    if questType in (_ET.BATTLE_QUEST, _ET.TOKEN_QUEST, _ET.PERSONAL_QUEST) and name == 'tokens':
        parentsName = quest.getParentsName()
        for n, v in value.iteritems():
            if n in parentsName:
                questNames = parentsName[n]
                if questNames:
                    v.update({'questNames': questNames})

    elif questType == _ET.PERSONAL_MISSION:
        ctx.update({'operationID': quest.getOperationID(),
         'chainID': quest.getChainID(),
         'campaignID': quest.getCampaignID(),
         'areTokensPawned': False})
    return _initFromTree(key, name, value, isCompensation, ctx=ctx)


def getTutorialBonuses(name, value):
    return _initFromTree((name,), name, value)


def getEventBoardsBonusObj(name, value):
    return _initFromTree((name, _ET.ELEN_QUEST), name, value)


def getNonQuestBonuses(name, value):
    return _initFromTree((name, 'default'), name, value)


def _getItemTooltip(name):
    header = i18n.makeString(TOOLTIPS.getAwardHeader(name))
    body = i18n.makeString(TOOLTIPS.getAwardBody(name))
    return makeTooltip(header or None, body or None) if header or body else ''


def mergeBonuses(bonuses):
    merged = copy.deepcopy(bonuses)
    if len(merged) > 1:
        i = 0
        while i < len(merged) - 1:
            j = i + 1
            while j < len(merged):
                mergFunc = getMergeBonusFunction(merged[i], merged[j])
                if mergFunc and merged[i].getName() == merged[j].getName():
                    merged[i] = mergFunc(merged[i], merged[j])
                    merged.pop(j)
                j += 1

            i += 1

    return merged


def getMergeBonusFunction(lhv, rhv):

    def hasOneBaseClass(l, r, cls):
        return isinstance(l, cls) and isinstance(r, cls)

    if hasOneBaseClass(lhv, lhv, ItemsBonus):
        return mergeItemsBonuses
    else:
        return mergeIntegralBonuses if hasOneBaseClass(lhv, rhv, IntegralBonus) or hasOneBaseClass(lhv, rhv, GoldBonus) else None


def mergeItemsBonuses(lhv, rhv):
    merged = copy.deepcopy(lhv)
    for key in merged.getValue():
        if key in rhv.getValue():
            merged.getValue()[key] += rhv.getValue()[key]

    for key, value in rhv.getValue().iteritems():
        if key not in merged.getValue():
            merged.getValue()[key] = value

    return merged


def mergeIntegralBonuses(lhv, rhv):
    merged = copy.deepcopy(lhv)
    merged.setValue(merged.getValue() + rhv.getValue())
    return merged
