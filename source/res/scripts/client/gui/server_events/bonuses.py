# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/bonuses.py
from collections import namedtuple
from functools import partial
import re
import BigWorld
from constants import EVENT_TYPE as _ET, DOSSIER_TYPE, PERSONAL_QUEST_FREE_TOKEN_NAME
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
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
from gui.Scaleform.settings import getBadgeIconPath, BADGES_ICONS
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
from items import vehicles, tankmen
from shared_utils import makeTupleByDict
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from gui.shared.tooltips import contexts
_CUSTOMIZATIONS_SCALE = 44.0 / 128
_EPIC_AWARD_STATIC_VO_ENTRIES = {'compensationTooltip': QUESTS.BONUSES_COMPENSATION,
 'hasCompensation': False,
 'align': 'center',
 'highlightType': '',
 'overlayType': ''}

def _augmentEpicAwardVOs(vos, titles=None, descriptions=None):
    for i in range(0, len(vos)):
        vos[i].update(_EPIC_AWARD_STATIC_VO_ENTRIES)
        if titles and titles[i]:
            vos[i]['title'] = titles[i]
        if descriptions and descriptions[i]:
            vos[i]['description'] = descriptions[i]

    return vos


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

    def __init__(self, name, value, isCompensation=False, ctx=None):
        self._name = name
        self._value = value
        self._isCompensation = isCompensation
        self._ctx = ctx or {}

    def getName(self):
        return self._name

    def getValue(self):
        return self._value

    def isCompensation(self):
        return self._isCompensation

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
        header = i18n.makeString(TOOLTIPS.getAwardHeader(self._name))
        body = i18n.makeString(TOOLTIPS.getAwardBody(self._name))
        return makeTooltip(header or None, body or None) if header or body else ''

    def getDescription(self):
        return i18n.makeString('#quests:bonuses/%s/description' % self._name, value=self.formatValue())

    def getList(self):
        return None

    def getRankedAwardVOs(self, iconSize='small', withCounts=False, withKey=False):
        itemInfo = {'imgSource': self.getIconBySize(iconSize),
         'label': self.getIconLabel(),
         'tooltip': self.getTooltip(),
         'align': TEXT_ALIGN.CENTER}
        if withKey:
            itemInfo['itemKey'] = self.getName()
        if withCounts:
            if isinstance(self._value, int):
                itemInfo['count'] = self._value
            else:
                itemInfo['count'] = 1
        return [itemInfo]

    def getEpicAwardVOs(self, withDescription=False):
        titles = [i18n.makeString(TOOLTIPS.getAwardHeader(self._name))] if withDescription else None
        descriptions = [i18n.makeString(TOOLTIPS.getAwardBody(self._name))] if withDescription else None
        vos = _augmentEpicAwardVOs(self.getRankedAwardVOs(iconSize='big'), titles=titles, descriptions=descriptions)
        return vos

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
            result[tID] = self._TOKEN_RECORD(tID, d.get('expires', {'at': None}).values()[0], d.get('count', 0), d.get('limit'))

        return result

    def getCount(self):
        return sum((v.get('count', 0) for v in self._value.values()))


class BattleTokensBonus(TokensBonus):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, name, value, isCompensation=False, ctx=None):
        super(TokensBonus, self).__init__(name, value, isCompensation)
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

    def _getUserName(self, styleID):
        webCache = self.eventsCache.prefetcher
        return i18n.makeString(webCache.getTokenInfo(styleID))


def personalMissionsTokensFactory(name, value, isCompensation=False, ctx=None):
    from gui.server_events.finders import PERSONAL_MISSION_TOKEN
    completionTokenID = PERSONAL_MISSION_TOKEN % ctx['operationID']
    result = []
    for tID, tValue in value.iteritems():
        if tID == PERSONAL_QUEST_FREE_TOKEN_NAME:
            result.append(FreeTokensBonus({tID: tValue}, isCompensation, ctx))
        if tID == completionTokenID:
            result.append(CompletionTokensBonus({tID: tValue}, isCompensation, ctx))
        result.append(TokensBonus(name, {tID: tValue}, isCompensation, ctx))

    return result


class FreeTokensBonus(TokensBonus):

    def __init__(self, value, isCompensation=False, ctx=None):
        super(FreeTokensBonus, self).__init__('freeTokens', value, isCompensation, ctx)

    def isShowInGUI(self):
        return self.getCount() > 0

    def formatValue(self):
        return str(self.getCount())

    def format(self):
        return makeHtmlString('html_templates:lobby/quests/bonuses', self._name, {'value': self.formatValue()})

    def areTokensPawned(self):
        return self.getContext()['areTokensPawned']


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

    def hasIconFormat(self):
        return True

    def getRankedAwardVOs(self, iconSize='small', withCounts=False, withKey=False):
        result = []
        for item, count in self.getItems().iteritems():
            itemInfo = {'imgSource': item.getBonusIcon(iconSize),
             'label': text_styles.stats('x{}'.format(count)),
             'tooltip': self.makeItemTooltip(item),
             'align': TEXT_ALIGN.RIGHT}
            if item.itemTypeName == 'optionalDevice':
                if item.isDeluxe():
                    itemInfo['highlightType'] = SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT
                    itemInfo['overlayType'] = SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS
            if withKey:
                itemInfo['itemKey'] = 'item_{}'.format(item.intCD)
            if withCounts:
                itemInfo['count'] = count
            result.append(itemInfo)

        return result

    def getEpicAwardVOs(self, withDescription=False):
        vos = _augmentEpicAwardVOs(self.getRankedAwardVOs(iconSize='big'))
        return vos

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

    def formattedList(self):
        result = []
        for booster, count in self.getBoosters().iteritems():
            if booster is not None:
                result.append(i18n.makeString('#quests:bonuses/boosters/name', name=booster.userName, quality=booster.qualityStr, count=count))

        for discount, count in self.getDiscounts().iteritems():
            if discount is not None:
                result.append(i18n.makeString('#quests:bonuses/discount/name', name=discount.userName, targetName=discount.targetName, effectValue=discount.getFormattedValue(), count=count))

        return result

    def getRankedAwardVOs(self, iconSize='small', withCounts=False, withKey=False):
        result = []
        for booster, count in self.getBoosters().iteritems():
            if booster is not None:
                itemData = {'imgSource': RES_ICONS.getBonusIcon(iconSize, booster.boosterGuiType),
                 'label': text_styles.hightlight('x{}'.format(count)),
                 'align': TEXT_ALIGN.RIGHT}
                itemData.update(self.__itemTooltip(booster))
                if withKey:
                    itemData['itemKey'] = 'booster_{}'.format(booster.boosterID)
                if withCounts:
                    itemData['count'] = count
                result.append(itemData)

        return result

    def getEpicAwardVOs(self, withDescription=False):
        titles = list() if withDescription and self._value.keys() else None
        descriptions = list() if withDescription and self._value.keys() else None
        if withDescription:
            bc = contexts.BoosterContext()
            for key in self._value.keys():
                boosterData = bc.buildItem(key)
                desc = re.sub('<(.*?)>', '', boosterData.description)
                descriptions.append(desc)
                titles.append(boosterData.userName)

        vos = _augmentEpicAwardVOs(self.getRankedAwardVOs(iconSize='big'), titles=titles, descriptions=descriptions)
        return vos

    @staticmethod
    def __itemTooltip(booster):
        return {'isSpecial': True,
         'specialAlias': TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO,
         'specialArgs': [booster.boosterID]}


class VehiclesBonus(SimpleBonus):
    DEFAULT_CREW_LVL = 50

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

    def getIcon(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_TANK

    def getTooltipIcon(self):
        vehicle, _ = self.getVehicles()[0]
        return vehicle.icon

    def getVehicles(self):
        result = []
        if self._value is not None:
            for intCD, vehInfo in self._value.iteritems():
                item = self.itemsCache.items.getItemByCD(intCD)
                if item is not None:
                    result.append((item, vehInfo))

        return result

    def compensation(self, vehicle):
        bonuses = []
        if not vehicle.isPurchased:
            return bonuses
        for curVehicle, vehInfo in self.getVehicles():
            compensation = vehInfo.get('customCompensation')
            if curVehicle == vehicle and compensation:
                money = Money.makeMoney(compensation)
                for currency, value in money.iteritems():
                    if value:
                        cls = _BONUSES.get(currency)
                        bonuses.append(cls(currency, value, isCompensation=True))

        return bonuses

    def getIconLabel(self):
        pass

    def getRankedAwardVOs(self, iconSize='small', withCounts=False, withKey=False):
        result = []
        for vehicle, vehInfo in self.getVehicles():
            vehicleVO = self.__getVehicleVO(vehicle, vehInfo, partial(RES_ICONS.getBonusIcon, iconSize))
            vehicleVO.update({'label': self.getIconLabel()})
            vehicleVO['align'] = TEXT_ALIGN.RIGHT
            if withKey:
                vehicleVO['itemKey'] = 'vehicle_{}'.format(vehicle.intCD)
            if withCounts:
                vehicleVO['count'] = 1
            result.append(vehicleVO)

        return result

    def getEpicAwardVOs(self):
        vos = _augmentEpicAwardVOs(self.getRankedAwardVOs(iconSize='big'))
        return vos

    @classmethod
    def getTmanRoleLevel(cls, vehInfo):
        if 'noCrew' not in vehInfo:
            if 'crewLvl' in vehInfo:
                return calculateRoleLevel(vehInfo.get('crewLvl', cls.DEFAULT_CREW_LVL), vehInfo.get('crewFreeXP', 0))
            if 'tankmen' in vehInfo:
                for tman in vehInfo['tankmen']:
                    if tman['role'] == Tankman.ROLES.COMMANDER:
                        return calculateRoleLevel(tman.get('roleLevel', cls.DEFAULT_CREW_LVL), tman.get('freeXP', 0))

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

    def getRankedAwardVOs(self, iconSize='small', withCounts=False, withKey=False):
        result = []
        badgesIconSizes = {'big': BADGES_ICONS.X80,
         'small': BADGES_ICONS.X48}
        for (block, record), _ in self.getRecords().iteritems():
            if _isBadge(block):
                header = i18n.makeString(BADGE.badgeName(record))
                body = i18n.makeString(BADGE.badgeDescriptor(record))
                note = i18n.makeString(BADGE.BADGE_NOTE)
                badgeVO = {'imgSource': getBadgeIconPath(badgesIconSizes[iconSize], record),
                 'label': '',
                 'tooltip': makeTooltip(header, body, note)}
                if withKey:
                    badgeVO['itemKey'] = BADGE.badgeName(record)
                if withCounts:
                    badgeVO['count'] = 1
                result.append(badgeVO)

        return result

    def getEpicAwardVOs(self, withDescription=False):
        titles = list() if withDescription and self._value.keys() else None
        descriptions = list() if withDescription and self._value.keys() else None
        if withDescription:
            for (block, record), _ in self.getRecords().iteritems():
                if _isBadge(block):
                    titles.append(i18n.makeString(BADGE.badgeName(record)))
                    descriptions.append(i18n.makeString(BADGE.badgeDescriptor(record)))

        vos = _augmentEpicAwardVOs(self.getRankedAwardVOs(iconSize='big'), titles=titles, descriptions=descriptions)
        return vos

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


class RefSystemTankmenBonus(TankmenBonus):

    def formatValue(self):
        result = []
        for tmanInfo in self.getTankmenData():
            if tmanInfo.isFemale:
                return '%s %s' % (i18n.makeString(QUESTS.BONUSES_ITEM_TANKWOMAN), i18n.makeString(QUESTS.BONUSES_TANKMEN_DESCRIPTION, value=getRoleUserName(tmanInfo.role)))
            result.append(i18n.makeString(QUESTS.BONUSES_TANKMEN_DESCRIPTION, value=getRoleUserName(tmanInfo.role)))

        return ', '.join(result)


class CustomizationsBonus(SimpleBonus):
    c11n = dependency.descriptor(ICustomizationService)
    INFOTIP_ARGS_ORDER = ('intCD', 'value', 'boundVehicle', 'boundToCurrentVehicle')

    def getList(self):
        result = []
        for itemData in self.getCustomizations():
            itemTypeName = itemData.get('custType')
            itemID = itemData.get('id')
            boundVehicle = itemData.get('vehTypeCompDescr')
            boundToCurrentVehicle = itemData.get('boundToCurrentVehicle', False)
            itemTypeID = GUI_ITEM_TYPE_INDICES.get(itemTypeName)
            item = self.c11n.getItemByID(itemTypeID, itemID)
            value = itemData.get('value', 0)
            valueStr = None
            if value > 1:
                valueStr = text_styles.main(i18n.makeString(QUESTS.BONUSES_CUSTOMIZATION_VALUE, count=value))
            result.append({'intCD': item.intCD,
             'texture': item.icon,
             'value': value,
             'valueStr': valueStr,
             'boundVehicle': boundVehicle,
             'boundToCurrentVehicle': boundToCurrentVehicle})

        return result

    def getCustomizations(self):
        return self._value or []

    def getRankedAwardVOs(self, iconSize='small', withCounts=False, withKey=False):
        result = []
        for item, data in zip(self.getCustomizations(), self.getList()):
            itemTypeName = item.get('custType')
            itemID = item.get('id')
            itemTypeID = GUI_ITEM_TYPE_INDICES.get(itemTypeName)
            c11nItem = self.c11n.getItemByID(itemTypeID, itemID)
            count = item.get('value', 1)
            itemData = {'imgSource': RES_ICONS.getBonusIcon(iconSize, c11nItem.itemTypeName),
             'label': text_styles.hightlight('x{}'.format(count)),
             'align': TEXT_ALIGN.RIGHT}
            itemData.update(self.__itemTooltip(data, isReceived=False))
            if withKey:
                itemData['itemKey'] = 'customization_{}'.format(item.get('custType'))
            if withCounts:
                itemData['count'] = count
            result.append(itemData)

        return result

    def getEpicAwardVOs(self, withDescription=False):
        titles = list() if withDescription and self._value else None
        descriptions = list() if withDescription and self._value else None
        if withDescription:
            for itemData in self.getCustomizations():
                itemTypeName = itemData.get('custType')
                itemID = itemData.get('id')
                itemTypeID = GUI_ITEM_TYPE_INDICES.get(itemTypeName)
                item = self.c11n.getItemByID(itemTypeID, itemID)
                descriptions.append(item.userType)
                titles.append(item.userName)

        vos = _augmentEpicAwardVOs(self.getRankedAwardVOs(iconSize='big'), titles=titles, descriptions=descriptions)
        return vos

    def __itemTooltip(self, data, isReceived):
        return {'isSpecial': True,
         'specialAlias': TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM,
         'specialArgs': [ data[o] for o in self.INFOTIP_ARGS_ORDER ] + [isReceived]}


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
 'tokens': {'default': TokensBonus,
            _ET.BATTLE_QUEST: BattleTokensBonus,
            _ET.TOKEN_QUEST: BattleTokensBonus,
            _ET.PERSONAL_QUEST: BattleTokensBonus,
            _ET.PERSONAL_MISSION: personalMissionsTokensFactory,
            _ET.ELEN_QUEST: BattleTokensBonus},
 'dossier': {'default': DossierBonus,
             _ET.PERSONAL_MISSION: PersonalMissionDossierBonus},
 'tankmen': {'default': TankmenBonus,
             _ET.PERSONAL_MISSION: TankwomanBonus,
             _ET.REF_SYSTEM_QUEST: RefSystemTankmenBonus},
 'customizations': CustomizationsBonus,
 'goodies': GoodiesBonus,
 'items': ItemsBonus,
 'oneof': BoxBonus,
 'badgesGroup': BadgesGroupBonus}
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


def getBonuses(quest, name, value, isCompensation=False):
    questType = quest.getType()
    key = [name, questType]
    ctx = {}
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
         'areTokensPawned': False})
    return _initFromTree(key, name, value, isCompensation, ctx)


def getTutorialBonuses(name, value):
    return _initFromTree((name,), name, value)


def getEventBoardsBonusObj(name, value):
    return _initFromTree((name, _ET.ELEN_QUEST), name, value)


def _getItemTooltip(name):
    header = i18n.makeString(TOOLTIPS.getAwardHeader(name))
    body = i18n.makeString(TOOLTIPS.getAwardBody(name))
    return makeTooltip(header or None, body or None) if header or body else ''
