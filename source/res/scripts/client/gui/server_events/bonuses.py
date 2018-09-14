# Embedded file name: scripts/client/gui/server_events/bonuses.py
from collections import namedtuple
import BigWorld
import Math
from constants import EVENT_TYPE as _ET
from gui.goodies.GoodiesCache import g_goodiesCache
from gui.shared.formatters import text_styles
from helpers import time_utils
from items import vehicles, tankmen
from gui.Scaleform.locale.QUESTS import QUESTS
from helpers import getLocalizedData, i18n
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK
from shared_utils import makeTupleByDict
from gui import makeHtmlString
from gui.shared import g_itemsCache
from gui.shared.gui_items.Tankman import getRoleUserName, calculateRoleLevel
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.genConsts.CUSTOMIZATION_ITEM_TYPE import CUSTOMIZATION_ITEM_TYPE

class SimpleBonus(object):

    def __init__(self, name, value):
        self._name = name
        self._value = value

    def getName(self):
        return self._name

    def getValue(self):
        return self._value

    def formatValue(self):
        if self._value:
            return str(self._value)
        else:
            return None

    def format(self):
        formattedValue = self.formatValue()
        if self._name is not None and formattedValue is not None:
            text = makeHtmlString('html_templates:lobby/quests/bonuses', self._name, {'value': formattedValue})
            if text != self._name:
                return text
        return formattedValue

    def formattedList(self):
        formattedObj = self.format()
        if formattedObj:
            return [formattedObj]
        return []

    def isShowInGUI(self):
        return True

    def getIcon(self):
        return ''

    def getTooltipIcon(self):
        return ''

    def getDescription(self):
        return i18n.makeString('#quests:bonuses/%s/description' % self._name, value=self.formatValue())


class FakeTextBonus(SimpleBonus):

    def __init__(self, value):
        super(FakeTextBonus, self).__init__('fakeText', value)


class IntegralBonus(SimpleBonus):

    def formatValue(self):
        if self._value:
            return BigWorld.wg_getIntegralFormat(self._value)
        else:
            return None


class FloatBonus(SimpleBonus):

    def formatValue(self):
        if self._value:
            return BigWorld.wg_getNiceNumberFormat(self._value)
        else:
            return None


class CreditsBonus(IntegralBonus):

    def getIcon(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_1

    def getTooltipIcon(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARD_CREDITS


class GoldBonus(SimpleBonus):

    def formatValue(self):
        if self._value:
            return BigWorld.wg_getGoldFormat(self._value)
        else:
            return None

    def getIcon(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_1


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

        if result:
            return ', '.join(result)
        else:
            return


class BoosterBonus(SimpleBonus):

    def getBoosters(self):
        boosters = {}
        if self._value is not None:
            _getBooster = g_goodiesCache.getBooster
            for boosterID, info in self._value.iteritems():
                booster = _getBooster(int(boosterID))
                if booster is not None:
                    boosters[booster] = info.get('count', 1)

        return boosters

    def format(self):
        result = []
        for booster, count in self.getBoosters().iteritems():
            if booster is not None:
                result.append(i18n.makeString('#quests:bonuses/boosters/name', name=booster.userName, quality=booster.qualityStr, count=count))

        if result:
            return ', '.join(result)
        else:
            return


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
            if 'noCrew' not in vehInfo:
                tmanRoleLevel = calculateRoleLevel(vehInfo.get('crewLvl', self.DEFAULT_CREW_LVL), vehInfo.get('crewFreeXP', 0))
            else:
                tmanRoleLevel = None
            vInfoLabels = []
            if 'rent' in vehInfo:
                rentDays = vehInfo.get('rent', {}).get('expires', {}).get('after', None)
                if rentDays:
                    rentDaysStr = makeHtmlString('html_templates:lobby/quests/bonuses', 'rentDays', {'value': str(rentDays)})
                    vInfoLabels.append(rentDaysStr)
            if tmanRoleLevel is not None:
                crewLvl = i18n.makeString('#quests:bonuses/vehicles/crewLvl', tmanRoleLevel)
                vInfoLabels.append(crewLvl)
            if len(vInfoLabels):
                result.append(text_styles.standard(i18n.makeString('#quests:bonuses/vehicles/name', name=text_styles.main(item.userName), vehInfo='; '.join(vInfoLabels))))
            else:
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


class DossierBonus(SimpleBonus):

    def getRecords(self):
        if self._value is not None:
            return set((name for name in self._value.iterkeys()))
        else:
            return set()

    def format(self):
        return ', '.join(self.formattedList())

    def formattedList(self):
        result = []
        for block, record in self.getRecords():
            try:
                if block in ACHIEVEMENT_BLOCK.ALL:
                    factory = getAchievementFactory((block, record))
                    if factory is not None:
                        achieve = factory.create()
                        if achieve is not None:
                            result.append(achieve.userName)
                else:
                    result.append(i18n.makeString('#quests:details/dossier/%s' % record))
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
        groups = {}
        for tmanInfo in self.getTankmenData():
            roleLevel = calculateRoleLevel(tmanInfo.roleLevel, tmanInfo.freeXP, typeID=(tmanInfo.nationID, tmanInfo.vehicleTypeID))
            if tmanInfo.vehicleTypeID not in groups:
                vehIntCD = vehicles.makeIntCompactDescrByID('vehicle', tmanInfo.nationID, tmanInfo.vehicleTypeID)
                groups[tmanInfo.vehicleTypeID] = {'vehName': g_itemsCache.items.getItemByCD(vehIntCD).shortUserName,
                 'skills': len(tmanInfo.skills),
                 'roleLevel': roleLevel}
            else:
                group = groups[tmanInfo.vehicleTypeID]
                group['skills'] += len(tmanInfo.skills)
                group['roleLevel'] = min(group['roleLevel'], roleLevel)

        result = []
        for group in groups.itervalues():
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
                else:
                    result.append(makeTupleByDict(self._TankmanInfoRecord, tankmanData))

        return result

    def getIcon(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_TANKMAN

    def getTooltipIcon(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_REFSYS_MEN_BW

    @classmethod
    def _makeTmanInfoByDescr(cls, td):
        return cls._TankmanInfoRecord(td.nationID, td.role, td.vehicleTypeID, td.firstNameID, -1, td.lastNameID, -1, td.iconID, -1, td.isPremium, td.roleLevel, td.freeXP, td.skills, td.isFemale, [])


class PotapovTankmenBonus(TankmenBonus):

    def formatValue(self):
        result = []
        for tmanInfo in self.getTankmenData():
            if tmanInfo.isFemale:
                result.append(i18n.makeString('#quests:bonuses/item/tankwoman'))
            else:
                result.append(i18n.makeString('#quests:bonuses/tankmen/description', value=getRoleUserName(tmanInfo.role)))

        return ', '.join(result)


class RefSystemTankmenBonus(TankmenBonus):

    def formatValue(self):
        result = []
        for tmanInfo in self.getTankmenData():
            result.append(i18n.makeString('#quests:bonuses/tankmen/description', value=getRoleUserName(tmanInfo.role)))

        return ', '.join(result)


class CustomizationsBonus(SimpleBonus):

    def _makeTextureUrl(self, width, height, texture, colors, armorColor):
        if texture is None or len(texture) == 0:
            return ''
        else:
            weights = Math.Vector4((colors[0] >> 24) / 255.0, (colors[1] >> 24) / 255.0, (colors[2] >> 24) / 255.0, (colors[3] >> 24) / 255.0)
            return 'img://camouflage,{0:d},{1:d},"{2:>s}",{3[0]:d},{3[1]:d},{3[2]:d},{3[3]:d},{4[0]:n},{4[1]:n},{4[2]:n},{4[3]:n},{5:d}'.format(width, height, texture, colors, weights, armorColor)

    def getList(self):
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
                    texture = self._makeTextureUrl(67, 67, camouflage.get('texture'), camouflage.get('colors', (0, 0, 0, 0)), armorColor)
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


_BONUSES = {'credits': CreditsBonus,
 'gold': GoldBonus,
 'xp': IntegralBonus,
 'freeXP': IntegralBonus,
 'tankmenXP': IntegralBonus,
 'xpFactor': FloatBonus,
 'creditsFactor': FloatBonus,
 'freeXPFactor': FloatBonus,
 'tankmenXPFactor': FloatBonus,
 'dailyXPFactor': FloatBonus,
 'items': ItemsBonus,
 'slots': IntegralBonus,
 'berths': IntegralBonus,
 'premium': IntegralBonus,
 'vehicles': VehiclesBonus,
 'meta': MetaBonus,
 'tokens': TokensBonus,
 'dossier': DossierBonus,
 'tankmen': TankmenBonus,
 'customizations': CustomizationsBonus,
 'goodies': BoosterBonus,
 'strBonus': SimpleBonus}
_BONUSES_BY_TYPE = {(_ET.POTAPOV_QUEST, 'tokens'): PotapovTokensBonus,
 (_ET.POTAPOV_QUEST, 'dossier'): PotapovDossierBonus,
 (_ET.POTAPOV_QUEST, 'tankmen'): PotapovTankmenBonus,
 (_ET.REF_SYSTEM_QUEST, 'tankmen'): RefSystemTankmenBonus}

def getBonusObj(quest, name, value):
    key = (quest.getType(), name)
    if key in _BONUSES_BY_TYPE:
        return _BONUSES_BY_TYPE[key](name, value)
    elif name in _BONUSES:
        return _BONUSES[name](name, value)
    else:
        return None


def getTutorialBonusObj(name, value):
    if name in _BONUSES:
        return _BONUSES[name](name, value)
    else:
        return None
