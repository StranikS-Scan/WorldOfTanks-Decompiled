# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/bonuses.py
from collections import namedtuple
import BigWorld
import Math
from constants import EVENT_TYPE as _ET, DOSSIER_TYPE
from gui.Scaleform.genConsts.BOOSTER_CONSTANTS import BOOSTER_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.goodies import g_goodiesCache
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
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
        formattedValue = self.formatValue()
        if self._name is not None and formattedValue is not None:
            text = makeHtmlString('html_templates:lobby/quests/bonuses', self._name, {'value': formattedValue})
            if text != self._name:
                return text
        return formattedValue

    def formattedList(self):
        formattedObj = self.format()
        return [formattedObj] if formattedObj else []

    def isShowInGUI(self):
        return True

    def getIcon(self):
        pass

    def getTooltipIcon(self):
        pass

    def getDescription(self):
        return i18n.makeString('#quests:bonuses/%s/description' % self._name, value=self.formatValue())

    def getList(self):
        return None

    def hasIconFormat(self):
        return False


class FakeTextBonus(SimpleBonus):

    def __init__(self, value):
        super(FakeTextBonus, self).__init__('fakeText', value)


class IntegralBonus(SimpleBonus):

    def formatValue(self):
        return BigWorld.wg_getIntegralFormat(self._value) if self._value else None


class FloatBonus(SimpleBonus):

    def formatValue(self):
        return BigWorld.wg_getNiceNumberFormat(self._value) if self._value else None


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
          'tooltip': TOOLTIPS.AWARDITEM_PREMDAYS}]

    def hasIconFormat(self):
        return True


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


class BoosterBonus(SimpleBonus):

    def getBoosters(self):
        boosters = {}
        if self._value is not None:
            _getBooster = g_goodiesCache.getBooster
            for boosterID, info in self._value.iteritems():
                booster = _getBooster(int(boosterID))
                if booster is not None and booster.enabled:
                    boosters[booster] = info.get('count', 1)

        return boosters

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

        return result

    def formattedList(self):
        result = []
        for booster, count in self.getBoosters().iteritems():
            if booster is not None:
                result.append(i18n.makeString('#quests:bonuses/boosters/name', name=booster.userName, quality=booster.qualityStr, count=count))

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
            if 'noCrew' not in vehInfo:
                tmanRoleLevel = calculateRoleLevel(vehInfo.get('crewLvl', self.DEFAULT_CREW_LVL), vehInfo.get('crewFreeXP', 0))
            else:
                tmanRoleLevel = None
            vInfoLabels = []
            if 'rent' in vehInfo:
                time = vehInfo.get('rent', {}).get('time', None)
                rentDays = None
                if time:
                    if time == float('inf'):
                        pass
                    elif time <= time_utils.DAYS_IN_YEAR:
                        rentDays = int(time)
                if rentDays:
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
                result.append(makeTupleByDict(self._TankmanInfoRecord, tankmanData))

        return result

    def getIcon(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_TANKMAN

    def getTooltipIcon(self):
        for tmanInfo in self.getTankmenData():
            if tmanInfo.isFemale:
                return RES_ICONS.MAPS_ICONS_QUESTS_TANKMANFEMALEGRAY

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
            result.append(i18n.makeString('#quests:bonuses/tankmen/description', value=getRoleUserName(tmanInfo.role)))

        return ', '.join(result)


class RefSystemTankmenBonus(TankmenBonus):

    def formatValue(self):
        result = []
        for tmanInfo in self.getTankmenData():
            if tmanInfo.isFemale:
                return '%s %s' % (i18n.makeString('#quests:bonuses/item/tankwoman'), i18n.makeString('#quests:bonuses/tankmen/description', value=getRoleUserName(tmanInfo.role)))
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
 'freeXP': FreeXpBonus,
 'tankmenXP': IntegralBonus,
 'xpFactor': FloatBonus,
 'creditsFactor': FloatBonus,
 'freeXPFactor': FloatBonus,
 'tankmenXPFactor': FloatBonus,
 'dailyXPFactor': FloatBonus,
 'items': ItemsBonus,
 'slots': IntegralBonus,
 'berths': IntegralBonus,
 'premium': PremiumDaysBonus,
 'vehicles': VehiclesBonus,
 'meta': MetaBonus,
 'tokens': {'default': TokensBonus,
            _ET.POTAPOV_QUEST: {'regular': PotapovTokensBonus,
                                'fallout': FalloutTokensBonus}},
 'dossier': {'default': DossierBonus,
             _ET.POTAPOV_QUEST: PotapovDossierBonus},
 'tankmen': {'default': TankmenBonus,
             _ET.POTAPOV_QUEST: PotapovTankmenBonus,
             _ET.REF_SYSTEM_QUEST: RefSystemTankmenBonus},
 'customizations': CustomizationsBonus,
 'goodies': BoosterBonus,
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
    if questType == _ET.POTAPOV_QUEST:
        key.append(quest.getQuestBranchName())
    return _initFromTree(key, name, value)


def getTutorialBonusObj(name, value):
    return _initFromTree((name,), name, value)
