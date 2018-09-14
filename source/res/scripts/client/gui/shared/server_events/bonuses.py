# Embedded file name: scripts/client/gui/shared/server_events/bonuses.py
import BigWorld
import Math
from gui.Scaleform.genConsts.CUSTOMIZATION_ITEM_TYPE import CUSTOMIZATION_ITEM_TYPE
from gui.shared.gui_items.Tankman import Tankman
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from helpers import getLocalizedData, i18n
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK
from gui import makeHtmlString
from gui.shared import g_itemsCache
from gui.shared.utils.functions import getTankmanRoleLevel
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from items import vehicles

class SimpleBonus(object):

    def __init__(self, name, value):
        self._name = name
        self._value = value

    def getName(self):
        return self._name

    def getValue(self):
        return self._value

    def formatValue(self):
        return str(self._value)

    def format(self):
        if self._name is not None:
            text = makeHtmlString('html_templates:lobby/quests/bonuses', self._name, {'value': self.formatValue()})
            if text != self._name:
                return text
        return self.formatValue()

    def formattedList(self):
        return [self.format()]

    def isShowInGUI(self):
        return True

    def getIcon(self):
        return ''

    def getTooltipIcon(self):
        return ''

    def getDescription(self):
        return i18n.makeString('#quests:bonuses/%s/description' % self._name, value=self.formatValue())


class IntegralBonus(SimpleBonus):

    def formatValue(self):
        return BigWorld.wg_getIntegralFormat(self._value)


class FloatBonus(SimpleBonus):

    def formatValue(self):
        return BigWorld.wg_getNiceNumberFormat(self._value)


class CreditsBonus(IntegralBonus):

    def getIcon(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_1

    def getTooltipIcon(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARD_CREDITS


class GoldBonus(SimpleBonus):

    def formatValue(self):
        return BigWorld.wg_getGoldFormat(self._value)

    def getIcon(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_1


class MetaBonus(SimpleBonus):

    def isShowInGUI(self):
        return False

    def formatValue(self):
        return getLocalizedData({'value': self._value}, 'value')


class TokensBonus(SimpleBonus):

    def isShowInGUI(self):
        return False

    def formatValue(self):
        return None

    def getTokens(self):
        return dict(((tID, d['expires']) for tID, d in self._value.iteritems()))


class ItemsBonus(SimpleBonus):

    def format(self):
        result = []
        if self._value is not None:
            for intCD, count in self._value.iteritems():
                item = g_itemsCache.items.getItemByCD(intCD)
                if item is not None:
                    result.append(i18n.makeString('#quests:bonuses/items/name', name=item.userName, count=count))

        return ', '.join(result)


class VehiclesBonus(SimpleBonus):
    DEFAULT_CREW_LVL = 50

    def formatValue(self):
        result = []
        for item, crew in self.getVehicles():
            result.append(item.shortUserName)

        return ', '.join(result)

    def format(self):
        return ', '.join(self.formattedList())

    def formattedList(self):
        result = []
        for item, crew in self.getVehicles():
            if 'noCrew' not in crew:
                tmanRoleLevel = getTankmanRoleLevel(crew.get('crewLvl', self.DEFAULT_CREW_LVL), crew.get('crewFreeXP', 0))
            else:
                tmanRoleLevel = None
            if tmanRoleLevel is not None:
                crewLvl = i18n.makeString('#quests:bonuses/vehicles/crewLvl', tmanRoleLevel)
                result.append(i18n.makeString('#quests:bonuses/vehicles/name', name=item.userName, crew=crewLvl))
            else:
                result.append(item.userName)

        return result

    def getIcon(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_TANK

    def getTooltipIcon(self):
        vehicle, _ = self.getVehicles()[0]
        return vehicle.icon

    def getVehicles(self):
        result = []
        if self._value is not None:
            for intCD, crew in self._value.iteritems():
                item = g_itemsCache.items.getItemByCD(intCD)
                if item is not None:
                    result.append((item, crew))

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


class TankmenBonus(SimpleBonus):

    def formatValue(self):
        result = []
        for item in self.getTankmen():
            result.append(item.roleUserName)

        return ', '.join(result)

    def getTankmen(self):
        result = []
        if self._value is not None:
            for tankmanCompactDescr in self._value:
                result.append(Tankman(tankmanCompactDescr))

        return result

    def getIcon(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_TANKMAN

    def getTooltipIcon(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_REFSYS_MEN_BW


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
                    _, _, texture, _, _, _ = emblem
                    res = {'id': itemId,
                     'type': CUSTOMIZATION_ITEM_TYPE.EMBLEM,
                     'nationId': 0,
                     'texture': texture}
            elif itemType == CUSTOMIZATION_ITEM_TYPE.INSCRIPTION_TYPE:
                customization = vehicles.g_cache.customization(itemId[0])
                inscriptions = customization.get(CUSTOMIZATION_ITEM_TYPE.INSCRIPTION_TYPE, {})
                inscription = inscriptions.get(itemId[1], None)
                if inscription:
                    _, _, texture, _, _, _ = inscription
                    nationId, itemId = itemId
            if texture.startswith('gui'):
                texture = texture.replace('gui', '..', 1)
            res = {'id': itemId,
             'type': CUSTOMIZATION_ITEM_TYPE.CI_TYPES.index(itemType),
             'nationId': nationId,
             'texture': texture,
             'isPermanent': item.get('isPermanent', False),
             'value': item.get('value', 0)}
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
 'customizations': CustomizationsBonus}

def getBonusObj(name, value):
    if name in _BONUSES:
        return _BONUSES[name](name, value)
    else:
        return None
