# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/bonuses.py
from collections import namedtuple
from functools import partial
import BigWorld
import Math
from constants import EVENT_TYPE as _ET, DOSSIER_TYPE
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK, BADGES_BLOCK
from gui import makeHtmlString
from gui.Scaleform.genConsts.BOOSTER_CONSTANTS import BOOSTER_CONSTANTS
from gui.Scaleform.genConsts.CUSTOMIZATION_ITEM_TYPE import CUSTOMIZATION_ITEM_TYPE
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.TEXT_ALIGN import TEXT_ALIGN
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.Scaleform.locale.BADGE import BADGE
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.settings import getBadgeIconPath, BADGES_ICONS
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import getRoleUserName, calculateRoleLevel
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from gui.shared.utils.functions import makeTooltip, stripColorTagDescrTags
from gui.shared.money import Currency, Money
from helpers import dependency
from helpers import getLocalizedData, i18n
from helpers import time_utils
from items import vehicles, tankmen
from shared_utils import makeTupleByDict
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
_CUSTOMIZATIONS_SCALE = 44.0 / 128

def _getAchievement(block, record, value):
    factory = getAchievementFactory((block, record))
    return factory.create(value=value)


def _isAchievement(block):
    return block in ACHIEVEMENT_BLOCK.ALL


class SimpleBonus(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, name, value, isCompensation=False):
        self._name = name
        self._value = value
        self._isCompensation = isCompensation

    def getName(self):
        return self._name

    def getValue(self):
        return self._value

    def isCompensation(self):
        return self._isCompensation

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
        """ Get award's tooltip for award carousel.
        """
        header = i18n.makeString(TOOLTIPS.getAwardHeader(self._name))
        body = i18n.makeString(TOOLTIPS.getAwardBody(self._name))
        if header or body:
            return makeTooltip(header or None, body or None)
        else:
            return ''
            return None

    def getDescription(self):
        return i18n.makeString('#quests:bonuses/%s/description' % self._name, value=self.formatValue())

    def getList(self):
        return None

    def getCarouselList(self, isReceived=False):
        """ Get list of VOs for award carousel.
        """
        return [{'label': self.carouselFormat(),
          'tooltip': self.getTooltip()}]

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

    def getIconBySize(self, size):
        iconName = RES_ICONS.getBonusIcon(size, self.getName())
        if iconName is None:
            iconName = RES_ICONS.getBonusIcon(size, 'default')
        return iconName

    def getIconLabel(self):
        """
        returns label which is displayed near icon. Originally used in ranked battles
        @return: styled label str
        """
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

    def formatValue(self):
        return BigWorld.wg_getIntegralFormat(self._value) if self._value else None


class FloatBonus(SimpleBonus):

    def formatValue(self):
        return BigWorld.wg_getNiceNumberFormat(self._value) if self._value else None


class CountableIntegralBonus(IntegralBonus):

    def getCarouselList(self, isReceived=False):
        return [{'imgSource': RES_ICONS.getAwardsCarouselIcon(self._name),
          'counter': text_styles.stats('x{}'.format(self._value)),
          'tooltip': self.getTooltip()}]


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

    def getCarouselList(self, isReceived=False):
        return [{'imgSource': RES_ICONS.getPremiumBonusesSmallIcon(self._value),
          'tooltip': self.getTooltip()}]

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


class BattleTokensBonus(TokensBonus):

    def __init__(self, name, value, isCompensation=False):
        super(TokensBonus, self).__init__(name, value, isCompensation)
        self._name = 'battleToken'

    def isShowInGUI(self):
        return True

    def getCarouselList(self, isReceived=False):
        return [{'imgSource': RES_ICONS.MAPS_ICONS_QUESTS_ICON_BATTLE_MISSIONS_PRIZE_TOKEN,
          'tooltip': self.getTooltip()}]


class PotapovTokensBonus(TokensBonus):

    def __init__(self, name, value, isCompensation=False):
        super(PotapovTokensBonus, self).__init__(name, value, isCompensation)
        self._name = 'potapovToken'
        self.__count = 0
        for tokenID, token in self._value.iteritems():
            self.__count += token['count']

    def isShowInGUI(self):
        return True

    def formatValue(self):
        return str(self.__count)

    def format(self):
        return makeHtmlString('html_templates:lobby/quests/bonuses', 'pqTokens', {'value': self.formatValue()})

    def getCarouselList(self, isReceived=False):
        return [{'imgSource': RES_ICONS.getAwardsCarouselIcon('tokens'),
          'counter': text_styles.stats('x{}'.format(self.__count)),
          'tooltip': self.getTooltip()}]


class FalloutTokensBonus(PotapovTokensBonus):

    def isShowInGUI(self):
        return False


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

    def getCarouselList(self, isReceived=False):
        result = []
        for item, count in self.getItems().iteritems():
            if item is not None and count:
                if item.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT and 'avatar' in item.tags:
                    alias = TOOLTIPS_CONSTANTS.BATTLE_CONSUMABLE
                elif item.itemTypeID == GUI_ITEM_TYPE.SHELL:
                    alias = TOOLTIPS_CONSTANTS.AWARD_SHELL
                else:
                    alias = TOOLTIPS_CONSTANTS.AWARD_MODULE
                result.append({'imgSource': item.icon,
                 'counter': text_styles.stats('x{}'.format(count)),
                 'isSpecial': True,
                 'specialAlias': alias,
                 'specialArgs': [item.intCD]})

        return result

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

    def getCarouselList(self, isReceived=False):
        result = []
        for booster, count in sorted(self.getBoosters().iteritems(), key=lambda (booster, count): booster.boosterType):
            if booster is not None:
                itemData = {'imgSource': booster.icon,
                 'counter': text_styles.stats('x{}'.format(count))}
                itemData.update(self.__itemTooltip(booster))
                result.append(itemData)

        for discount, count in sorted(self.getDiscounts().iteritems()):
            result.append({'imgSource': discount.icon,
             'counter': discount.getFormattedValue(text_styles.stats),
             'tooltip': makeTooltip(header=discount.userName, body=discount.description)})

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

    @staticmethod
    def __itemTooltip(booster):
        return {'isSpecial': True,
         'specialAlias': TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO,
         'specialArgs': [booster.boosterID]}


class VehiclesBonus(SimpleBonus):
    DEFAULT_CREW_LVL = 50

    def formatValue(self):
        result = []
        for item, vehInfo in self.getVehicles():
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
            if len(vInfoLabels):
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
        """ Get compensation bonuses for the given vehicle.
        """
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

    def getCarouselList(self, isReceived=False):
        result = []
        for vehicle, vehInfo in self.getVehicles():
            result.append(self.__getVehicleVO(vehicle, vehInfo, RES_ICONS.getAwardsCarouselIcon))

        return result

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

    @classmethod
    def getTmanRoleLevel(cls, vehInfo):
        if 'noCrew' not in vehInfo:
            return calculateRoleLevel(vehInfo.get('crewLvl', cls.DEFAULT_CREW_LVL), vehInfo.get('crewFreeXP', 0))
        else:
            return None
            return None

    @staticmethod
    def getRentDays(vehInfo):
        """ Get rent days info from bonus if there is such info.
        """
        if 'rent' not in vehInfo:
            return None
        else:
            time = vehInfo.get('rent', {}).get('time')
            if time:
                if time == float('inf'):
                    return None
                elif time <= time_utils.DAYS_IN_YEAR:
                    return int(time)
                else:
                    return None
            return None

    @staticmethod
    def getRentBattles(vehInfo):
        """ Get rent battles info from bonus if there is such info.
        
        Rent battles means rent vehicle for a given number of battles.
        """
        return vehInfo.get('rent', {}).get('battles')

    @staticmethod
    def getRentWins(vehInfo):
        """ Get rent wins info from bonus if there is such info.
        
        Rent battles means rent vehicle for a given number of wins (lost battles don't count).
        """
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


class DossierBonus(SimpleBonus):

    def getRecords(self):
        """ Returns dictionary of dossier records {(dossier_block, record_name): record_value), ....}
        """
        records = {}
        if self._value is not None:
            for dossierType in self._value:
                if dossierType != DOSSIER_TYPE.CLAN:
                    for name, data in self._value[dossierType].iteritems():
                        records[name] = data.get('value', 0)

        return records

    def getAchievements(self):
        result = []
        for (block, record), value in self.getRecords().iteritems():
            if _isAchievement(block):
                if block == ACHIEVEMENT_BLOCK.RARE:
                    continue
                try:
                    result.append(_getAchievement(block, record, value))
                except Exception:
                    LOG_ERROR('There is error while getting bonus dossier record name')
                    LOG_CURRENT_EXCEPTION()

        return result

    def format(self):
        return ', '.join(self.formattedList())

    def formattedList(self):
        result = []
        for (block, record), value in self.getRecords().iteritems():
            try:
                if _isAchievement(block):
                    if block == ACHIEVEMENT_BLOCK.RARE:
                        continue
                    achieve = _getAchievement(block, record, value)
                    result.append(achieve.userName)
                else:
                    result.append(i18n.makeString('#quests:details/dossier/%s' % record))
            except Exception:
                LOG_ERROR('There is error while getting bonus dossier record name')
                LOG_CURRENT_EXCEPTION()

        return result

    def getCarouselList(self, isReceived=False):
        result = []
        for (block, record), value in self.getRecords().iteritems():
            try:
                if _isAchievement(block):
                    if block == ACHIEVEMENT_BLOCK.RARE:
                        continue
                    achievement = _getAchievement(block, record, value)
                    result.append({'imgSource': achievement.getSmallIcon(),
                     'isSpecial': True,
                     'specialAlias': TOOLTIPS_CONSTANTS.BATTLE_STATS_ACHIEVS,
                     'specialArgs': [block, record, value]})
            except Exception:
                LOG_ERROR('There is error while getting bonus dossier record name')
                LOG_CURRENT_EXCEPTION()

        return result

    def getRankedAwardVOs(self, iconSize='small', withCounts=False, withKey=False):
        """
        Here we're supporting bonuses only that allowed in ranked battles
        """
        result = []
        badgesIconSizes = {'big': BADGES_ICONS.X80,
         'small': BADGES_ICONS.X48}
        for (block, record), value in self.getRecords().iteritems():
            if block == BADGES_BLOCK:
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


class PotapovDossierBonus(DossierBonus):

    def isShowInGUI(self):
        return False


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
                if type(tankmanData) is str:
                    result.append(self._makeTmanInfoByDescr(tankmen.TankmanDescr(compactDescr=tankmanData)))
                result.append(makeTupleByDict(self._TankmanInfoRecord, tankmanData))

        return result

    def getTankmenGroups(self):
        """ Create groups by vehicle.
        """
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

    def getCarouselList(self, isReceived=False):
        result = []
        for group in self.getTankmenGroups().itervalues():
            if group['skills']:
                key = '#quests:bonuses/item/tankmen/with_skills'
            else:
                key = '#quests:bonuses/item/tankmen/no_skills'
            tooltip = makeTooltip(TOOLTIPS.getAwardHeader(self._name), i18n.makeString(key, **group))
            result.append({'imgSource': RES_ICONS.MAPS_ICONS_LIBRARY_BONUSES_TANKMEN,
             'tooltip': tooltip})

        return result

    @classmethod
    def _makeTmanInfoByDescr(cls, td):
        return cls._TankmanInfoRecord(td.nationID, td.role, td.vehicleTypeID, td.firstNameID, -1, td.lastNameID, -1, td.iconID, -1, td.isPremium, td.roleLevel, td.freeXP, td.skills, td.isFemale, [])


class PotapovTankmenBonus(TankmenBonus):

    def __init__(self, name, value, isCompensation=False):
        super(PotapovTankmenBonus, self).__init__(name, value, isCompensation)
        self._name = 'potapovTankmen'

    def formatValue(self):
        result = []
        for tmanInfo in self.getTankmenData():
            if tmanInfo.isFemale:
                result.append(i18n.makeString('#quests:bonuses/item/tankwoman'))
            result.append(i18n.makeString('#quests:bonuses/tankmen/description', value=getRoleUserName(tmanInfo.role)))

        return ', '.join(result)

    def getCarouselList(self, isReceived=False):
        result = []
        for tmanInfo in self.getTankmenData():
            if tmanInfo.isFemale:
                tooltip = makeTooltip(TOOLTIPS.AWARDITEM_TANKWOMEN_HEADER, TOOLTIPS.AWARDITEM_TANKWOMEN_BODY)
            else:
                tooltip = makeTooltip(i18n.makeString(QUESTS.BONUSES_TANKMEN_DESCRIPTION, value=getRoleUserName(tmanInfo.role)))
            result.append({'imgSource': RES_ICONS.MAPS_ICONS_LIBRARY_BONUSES_TANKWOMEN,
             'tooltip': tooltip})

        return result


class RefSystemTankmenBonus(TankmenBonus):

    def formatValue(self):
        result = []
        for tmanInfo in self.getTankmenData():
            if tmanInfo.isFemale:
                return '%s %s' % (i18n.makeString('#quests:bonuses/item/tankwoman'), i18n.makeString('#quests:bonuses/tankmen/description', value=getRoleUserName(tmanInfo.role)))
            result.append(i18n.makeString('#quests:bonuses/tankmen/description', value=getRoleUserName(tmanInfo.role)))

        return ', '.join(result)


class CustomizationsBonus(SimpleBonus):
    INFOTIP_ARGS_ORDER = ('type', 'id', 'nationId', 'value', 'isPermanent', 'boundVehicle', 'boundToCurrentVehicle')

    def _makeTextureUrl(self, width, height, texture, colors, armorColor):
        if texture is None or len(texture) == 0:
            return ''
        else:
            weights = Math.Vector4((colors[0] >> 24) / 255.0, (colors[1] >> 24) / 255.0, (colors[2] >> 24) / 255.0, (colors[3] >> 24) / 255.0)
            return 'img://camouflage,{0:d},{1:d},"{2:>s}",{3[0]:d},{3[1]:d},{3[2]:d},{3[3]:d},{4[0]:n},{4[1]:n},{4[2]:n},{4[3]:n},{5:d}'.format(width, height, texture, colors, weights, armorColor)

    def getList(self, defaultSize=67):
        result = []
        for item in self.getCustomizations():
            itemType = item.get('custType')
            itemId = item.get('id', (-1, -1))
            boundVehicle = item.get('vehTypeCompDescr', None)
            boundToCurrentVehicle = item.get('boundToCurrentVehicle', False)
            nationId = 0
            texture = ''
            if itemType == CUSTOMIZATION_ITEM_TYPE.CAMOUFLAGE_TYPE:
                customization = vehicles.g_cache.customization(itemId[0])
                camouflages = customization.get('camouflages', {})
                camouflage = camouflages.get(itemId[1], None)
                if camouflage:
                    armorColor = customization.get('armorColor', 0)
                    texture = self._makeTextureUrl(defaultSize, defaultSize, camouflage.get('texture'), camouflage.get('colors', (0, 0, 0, 0)), armorColor)
                    nationId, itemId = itemId
            elif itemType == CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE:
                _, emblems, _ = vehicles.g_cache.playerEmblems()
                emblem = emblems.get(itemId, None)
                if emblem:
                    texture = emblem[2]
            elif itemType == CUSTOMIZATION_ITEM_TYPE.INSCRIPTION_TYPE:
                customization = vehicles.g_cache.customization(itemId[0])
                inscriptions = customization.get(CUSTOMIZATION_ITEM_TYPE.INSCRIPTION_TYPE, {})
                inscription = inscriptions.get(itemId[1], None)
                if inscription:
                    texture = inscription[2]
                    nationId, itemId = itemId
            if texture.startswith('gui'):
                texture = texture.replace('gui', '..', 1)
            isPermanent = item.get('isPermanent', False)
            value = item.get('value', 0)
            valueStr = None
            if not isPermanent:
                value *= time_utils.ONE_DAY
            elif value > 1:
                valueStr = text_styles.main(i18n.makeString(QUESTS.BONUSES_CUSTOMIZATION_VALUE, count=value))
            res = {'id': itemId,
             'type': CUSTOMIZATION_ITEM_TYPE.CI_TYPES.index(itemType),
             'nationId': nationId,
             'texture': texture,
             'isPermanent': isPermanent,
             'value': value,
             'valueStr': valueStr,
             'boundVehicle': boundVehicle,
             'boundToCurrentVehicle': boundToCurrentVehicle}
            result.append(res)

        return result

    def getCustomizations(self):
        return self._value or []

    def getCarouselList(self, isReceived=False):
        result = []
        for item, data in zip(self.getCustomizations(), self.getList(defaultSize=128)):
            itemData = {'imgSource': data.get('texture'),
             'scaleImg': _CUSTOMIZATIONS_SCALE,
             'counter': text_styles.stats('x{}'.format(item.get('value')))}
            itemData.update(self.__itemTooltip(data, isReceived))
            result.append(itemData)

        return result

    def getRankedAwardVOs(self, iconSize='small', withCounts=False, withKey=False):
        result = []
        for item, data in zip(self.getCustomizations(), self.getList(defaultSize=128)):
            count = item.get('value', 1)
            itemData = {'imgSource': RES_ICONS.getBonusIcon(iconSize, item.get('custType')),
             'label': text_styles.hightlight('x{}'.format(count)),
             'align': TEXT_ALIGN.RIGHT}
            itemData.update(self.__itemTooltip(data, isReceived=False))
            if withKey:
                itemData['itemKey'] = 'customization_{}'.format(item.get('custType'))
            if withCounts:
                itemData['count'] = count
            result.append(itemData)

        return result

    def __itemTooltip(self, data, isReceived):
        return {'isSpecial': True,
         'specialAlias': TOOLTIPS_CONSTANTS.CUSTOMIZATION_ITEM,
         'specialArgs': [ data[o] for o in self.INFOTIP_ARGS_ORDER ] + [isReceived]}


class BoxBonus(SimpleBonus):
    __rankedIconSizes = {'big': '450x400',
     'small': '100x88'}

    class HANDLER_NAMES:
        RANKED = 'ranked'

    def __init__(self, name, value, isCompensation=False):
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
            _ET.POTAPOV_QUEST: {'regular': PotapovTokensBonus,
                                'fallout': FalloutTokensBonus}},
 'dossier': {'default': DossierBonus,
             _ET.POTAPOV_QUEST: PotapovDossierBonus},
 'tankmen': {'default': TankmenBonus,
             _ET.POTAPOV_QUEST: PotapovTankmenBonus,
             _ET.REF_SYSTEM_QUEST: RefSystemTankmenBonus},
 'customizations': CustomizationsBonus,
 'goodies': GoodiesBonus,
 'items': ItemsBonus,
 'oneof': BoxBonus}
_BONUSES_PRIORITY = ('tokens', 'oneof')
_BONUSES_ORDER = dict(((n, idx) for idx, n in enumerate(_BONUSES_PRIORITY)))

def compareBonuses(bonusName1, bonusName2):
    if bonusName1 not in _BONUSES_ORDER and bonusName2 not in _BONUSES_ORDER:
        return cmp(bonusName1, bonusName2)
    if bonusName1 not in _BONUSES_ORDER:
        return 1
    return -1 if bonusName2 not in _BONUSES_ORDER else _BONUSES_ORDER[bonusName1] - _BONUSES_ORDER[bonusName2]


def _getClassFromTree(tree, path):
    if not tree or not path:
        return
    else:
        key = path[0]
        subTree = None
        if key in tree:
            subTree = tree[key]
        elif 'default' in tree:
            subTree = tree['default']
        if type(subTree) is dict:
            return _getClassFromTree(subTree, path[1:])
        return subTree
        return


def _initFromTree(key, name, value, isCompensation=False):
    bonus = None
    clazz = _getClassFromTree(_BONUSES, key)
    if clazz is not None:
        bonus = clazz(name, value, isCompensation)
    return bonus


def getBonusObj(quest, name, value, isCompensation=False):
    """ Returns corresponding bonus object with given name
    """
    questType = quest.getType()
    key = [name, questType]
    if questType in (_ET.BATTLE_QUEST, _ET.TOKEN_QUEST, _ET.PERSONAL_QUEST) and name == 'tokens':
        parentsName = quest.getParentsName()
        for n, v in value.iteritems():
            if n in parentsName:
                questNames = parentsName[n]
                if questNames:
                    v.update({'questNames': questNames})

    elif questType == _ET.POTAPOV_QUEST:
        key.append(quest.getQuestBranchName())
    return _initFromTree(key, name, value, isCompensation)


def getTutorialBonusObj(name, value):
    return _initFromTree((name,), name, value)


def _getItemTooltip(name):
    header = i18n.makeString(TOOLTIPS.getAwardHeader(name))
    body = i18n.makeString(TOOLTIPS.getAwardBody(name))
    if header or body:
        return makeTooltip(header or None, body or None)
    else:
        return ''
        return None
