# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/bonuses.py
from collections import namedtuple
import BigWorld
import Math
from constants import EVENT_TYPE as _ET, DOSSIER_TYPE
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK
from gui import makeHtmlString
from gui.Scaleform.genConsts.BOOSTER_CONSTANTS import BOOSTER_CONSTANTS
from gui.Scaleform.genConsts.CUSTOMIZATION_ITEM_TYPE import CUSTOMIZATION_ITEM_TYPE
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.goodies import g_goodiesCache
from gui.shared import g_itemsCache
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import getRoleUserName, calculateRoleLevel
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from gui.shared.utils.functions import makeTooltip
from helpers import getLocalizedData, i18n
from helpers import time_utils
from items import vehicles, tankmen
from shared_utils import makeTupleByDict
_CUSTOMIZATIONS_SCALE = 44.0 / 128

def _getAchievement(block, record, value):
    factory = getAchievementFactory((block, record))
    return factory.create(value=value)


def _isAchievement(block):
    return block in ACHIEVEMENT_BLOCK.ALL


class SimpleBonus(object):

    def __init__(self, name, value):
        self._name = name
        self._value = value

    def getName(self):
        return self._name

    def getValue(self):
        return self._value

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
          'itemSource': RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICONBIG_1,
          'tooltip': TOOLTIPS.AWARDITEM_CREDITS}]

    def hasIconFormat(self):
        return True


class GoldBonus(SimpleBonus):

    def formatValue(self):
        return BigWorld.wg_getGoldFormat(self._value) if self._value else None

    def getIcon(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_1

    def getList(self):
        return [{'value': self.formatValue(),
          'itemSource': RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICONBIG,
          'tooltip': TOOLTIPS.AWARDITEM_GOLD}]

    def hasIconFormat(self):
        return True


class FreeXpBonus(IntegralBonus):

    def getList(self):
        return [{'value': self.formatValue(),
          'itemSource': RES_ICONS.MAPS_ICONS_LIBRARY_FREEXPICONBIG,
          'tooltip': TOOLTIPS.AWARDITEM_FREEXP}]

    def hasIconFormat(self):
        return True


class PremiumDaysBonus(IntegralBonus):

    def getList(self):
        return [{'itemSource': RES_ICONS.MAPS_ICONS_LIBRARY_PREMDAYICONBIG,
          'tooltip': TOOLTIPS.AWARDITEM_PREMIUM}]

    def hasIconFormat(self):
        return True

    def getCarouselList(self, isReceived=False):
        return [{'imgSource': RES_ICONS.getPremiumCarouselIcon(self._value),
          'tooltip': self.getTooltip()}]


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

    def __init__(self, name, value):
        super(TokensBonus, self).__init__(name, value)
        self._name = 'battleToken'

    def isShowInGUI(self):
        return self.__getFirstQuestName() != ''

    def getCarouselList(self, isReceived=False):
        return [{'imgSource': RES_ICONS.MAPS_ICONS_QUESTS_ICON_BATTLE_MISSIONS_PRIZE_TOKEN,
          'tooltip': self.getTooltip()}]

    def getTooltip(self):
        """ Get award's tooltip for award carousel.
        """
        if len(self._value) > 1 or len(self._value.values()[0].get('questNames', [])) > 1:
            nameFormat = '{}/several'.format(self._name)
            header = i18n.makeString(TOOLTIPS.getAwardHeader(nameFormat))
            body = self.__getAllQuestNames()
        else:
            nameFormat = '{}/one'.format(self._name)
            header = i18n.makeString(TOOLTIPS.getAwardHeader(nameFormat))
            body = i18n.makeString(TOOLTIPS.getAwardBody(nameFormat), name=self.__getFirstQuestName())
        if header or body:
            return makeTooltip(header or None, body or None)
        else:
            return ''
            return None

    def __getAllQuestNames(self):
        """Return formatted string for tooltip with several quest
        1. "quest name 1"
        2. "quest name 2"
        ...
        :return:
        """
        tooltip = [i18n.makeString(TOOLTIPS.AWARDITEM_BATTLETOKEN_SEVERAL_BODY)]
        questIdx = 0
        for item in self._value.values():
            names = item.get('questNames', [])
            for name in names:
                if name:
                    questIdx += 1
                    tooltip.append(i18n.makeString(TOOLTIPS.AWARDITEM_BATTLETOKEN_SEVERAL_LINE, num=questIdx, name=name))

        return '\n'.join(tooltip)

    def __getFirstQuestName(self):
        """We're show only one (first) quest in tooltip
        :return:
        """
        if len(self._value) > 0:
            _, firstItem = self._value.items()[0]
            if firstItem:
                names = firstItem.get('questNames', [])
                if len(names) > 0:
                    return names[0]


class PotapovTokensBonus(TokensBonus):

    def __init__(self, name, value):
        super(PotapovTokensBonus, self).__init__(name, value)
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
        return [{'imgSource': RES_ICONS.getAwardsCarouselIcon(self._name),
          'counter': text_styles.stats('x{}'.format(self.__count)),
          'tooltip': self.getTooltip()}]


class FalloutTokensBonus(PotapovTokensBonus):

    def isShowInGUI(self):
        return False


class ItemsBonus(SimpleBonus):

    def getItems(self):
        if self._value is not None:
            _getItem = g_itemsCache.items.getItemByCD
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
                tooltip = makeTooltip(header=item.userName, body=item.fullDescription)
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


class GoodiesBonus(SimpleBonus):

    def getBoosters(self):
        return self._getGoodies(g_goodiesCache.getBooster)

    def getDiscounts(self):
        return self._getGoodies(g_goodiesCache.getDiscount)

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
                result.append({'imgSource': booster.icon,
                 'counter': text_styles.stats('x{}'.format(count)),
                 'isSpecial': True,
                 'specialAlias': TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO,
                 'specialArgs': [booster.boosterID]})

        for discount, count in sorted(self.getDiscounts().iteritems()):
            result.append({'imgSource': discount.icon,
             'counter': discount.getFormattedValue(text_styles.stats),
             'tooltip': makeTooltip(header=discount.userName, body=discount.description)})

        return result


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
            tmanRoleLevel = self.__getTmanRoleLevel(vehInfo)
            rentDays = self.__getRentDays(vehInfo)
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
                item = g_itemsCache.items.getItemByCD(intCD)
                if item is not None:
                    result.append((item, vehInfo))

        return result

    def getCarouselList(self, isReceived=False):
        result = []
        for vehicle, vehInfo in self.getVehicles():
            tmanRoleLevel = self.__getTmanRoleLevel(vehInfo)
            rentDays = self.__getRentDays(vehInfo)
            if rentDays:
                image = RES_ICONS.MAPS_ICONS_LIBRARY_BONUSES_VEHICLES_RENT
                rentExpiryTime = time_utils.getCurrentTimestamp()
                rentExpiryTime += rentDays * time_utils.ONE_DAY
            else:
                image = RES_ICONS.MAPS_ICONS_LIBRARY_BONUSES_VEHICLES
                rentExpiryTime = 0
            result.append({'imgSource': image,
             'isSpecial': True,
             'specialAlias': TOOLTIPS_CONSTANTS.AWARD_VEHICLE,
             'specialArgs': [vehicle.intCD, tmanRoleLevel, rentExpiryTime]})

        return result

    @classmethod
    def __getTmanRoleLevel(cls, vehInfo):
        if 'noCrew' not in vehInfo:
            return calculateRoleLevel(vehInfo.get('crewLvl', cls.DEFAULT_CREW_LVL), vehInfo.get('crewFreeXP', 0))
        else:
            return None
            return None

    @staticmethod
    def __getRentDays(vehInfo):
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
                groups[tmanInfo.vehicleTypeID] = {'vehName': g_itemsCache.items.getItemByCD(vehIntCD).shortUserName,
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
            res = ''
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
                    res = {'id': itemId,
                     'type': CUSTOMIZATION_ITEM_TYPE.EMBLEM,
                     'nationId': 0,
                     'texture': texture}
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
        result = []
        if self._value is not None:
            for item in self._value:
                result.append(item)

        return result

    def getCarouselList(self, isReceived=False):
        result = []
        for item, data in zip(self.getCustomizations(), self.getList(defaultSize=128)):
            result.append({'imgSource': data.get('texture'),
             'scaleImg': _CUSTOMIZATIONS_SCALE,
             'counter': text_styles.stats('x{}'.format(item.get('value'))),
             'isSpecial': True,
             'specialAlias': TOOLTIPS_CONSTANTS.CUSTOMIZATION_ITEM,
             'specialArgs': [ data[o] for o in self.INFOTIP_ARGS_ORDER ] + [isReceived]})

        return result


_BONUSES = {'credits': CreditsBonus,
 'gold': GoldBonus,
 'xp': IntegralBonus,
 'freeXP': FreeXpBonus,
 'tankmenXP': IntegralBonus,
 'xpFactor': FloatBonus,
 'creditsFactor': FloatBonus,
 'freeXPFactor': FloatBonus,
 'tankmenXPFactor': FloatBonus,
 'dailyXPFactor': FloatBonus,
 'items': ItemsBonus,
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
 'strBonus': SimpleBonus}
_BONUSES_PRIORITY = ('tokens',)
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


def _initFromTree(key, name, value):
    bonus = None
    clazz = _getClassFromTree(_BONUSES, key)
    if clazz is not None:
        bonus = clazz(name, value)
    return bonus


def getBonusObj(quest, name, value):
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
    return _initFromTree(key, name, value)


def getTutorialBonusObj(name, value):
    return _initFromTree((name,), name, value)
