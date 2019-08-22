# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/__init__.py
import sys
import weakref
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.Scaleform.daapi.view.lobby.techtree.settings import UNKNOWN_VEHICLE_LEVEL, UnlockProps
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.app_loader import sf_lobby
from gui.shared.formatters import icons
from helpers import dependency
from helpers.i18n import makeString
from items import vehicles
from shared_utils import CONST_CONTAINER
from skeletons.gui.shared import IItemsCache

class TOOLTIP_TYPE(CONST_CONTAINER):
    VEHICLE = 'vehicle'
    TANKMAN = 'tankman'
    NOT_RECRUITED_TANKMAN = 'notRecruitedTankman'
    SKILL = 'skill'
    CREW_SKIN = 'crew_skin'
    CREW_BOOK = 'crew_book'
    ACHIEVEMENT = 'achievement'
    ACHIEVEMENT_ATTR = 'achievementAttr'
    MODULE = 'module'
    SHELL = 'shell'
    EQUIPMENT = 'equipment'
    EFFICIENCY = 'efficiency'
    FORTIFICATIONS = 'fortification'
    IGR = 'igr'
    CYBER_SPORT = 'cyberSport'
    MAP = 'map'
    CONTROL = 'control'
    PRIVATE_QUESTS = 'privateQuests'
    CONTACT = 'contact'
    QUESTS = 'quests'
    HANGAR_TUTORIAL = 'hangarTutorial'
    CLAN_PROFILE = 'clanProfile'
    TECH_CUSTOMIZATION = 'techCustomization'
    BOOSTER = 'booster'
    VEHICLE_FILTER = 'vehicleFilter'
    VEH_CMP_CUSTOMIZATION = 'vehCmpCustomization'
    RESERVE = 'reserve'
    RANKED_STEP = 'rankedStep'
    RANKED_RANK = 'rankedRank'
    RANKED_CALENDAR_DAY = 'rankedCalendarDayInfo'
    RANKED_SELECTOR_INFO = 'rankedSelectorInfo'
    RANKED_DIVISION_INFO = 'rankedDivisionInfo'
    RANKED_YEAR_REWARD = 'rankedYearReward'
    BATTLE_ROYALE_PRIME_TIMES = 'battleRoyalePrimeTimes'
    BATTLE_ROYALE_STEP = 'battleRoyaleStep'
    BATTLE_ROYALE_TITLE = 'battleRoyaleTitle'
    BATTLE_ROYALE_SELECTOR_INFO = 'battleRoyaleSelectorInfo'
    FAKE = 'fake'
    VEHICLE_ELITE_BONUS = 'vehicleEliteBonus'
    VEHICLE_HISTORICAL_REFERENCE = 'vehicleHistoricalReference'
    MARATHON = 'marathon'
    EPIC_SKILL_INFO = 'epicSkillInfo'
    EPIC_SELECTOR_INFO = 'epicSelectorInfo'
    EPIC_SELECTOR_UNAVAILABLE_INFO = 'epicSelectorUnavailableInfo'
    EPIC_META_LEVEL_PROGRESS_INFO = 'epicMetaLevelProgressInfo'
    EPIC_PRESTIGE_PROGRESS_BLOCK_INFO = 'epicPrestigeProgressBlockInfo'
    BLUEPRINTS = 'blueprintsInfo'
    FRONTLINE = 'frontlineInfo'
    SQUAD_BONUS = 'squadBonus'
    SESSION_STATS = 'sessionStats'
    FESTIVAL_ITEMS = 'festivalItemsInfo'


class TOOLTIP_COMPONENT(CONST_CONTAINER):
    TECH_MAIN = 'technical_maintenance'
    HANGAR = 'hangar'
    SHOP = 'shop'
    INVENTORY = 'inventory'
    PERSONAL_CASE = 'personal_case'
    CAROUSEL = 'carousel'
    RESEARCH = 'research'
    PROFILE = 'profile'
    PROFILE_VEHICLE = 'profileVehicle'
    FINAL_STATISTIC = 'FinalStatistic'
    CYBER_SPORT_UNIT = 'CyberSportUnit'
    FORTIFICATIONS = 'fortification'
    CLAN_PROFILE = 'clanProfile'
    SETTINGS = 'settings'
    CUSTOMIZATION = 'customization'
    CONTACT = 'contact'
    HANGAR_TUTORIAL = 'hangarTutorial'
    TECH_CUSTOMIZATION = 'techCustomization'
    BOOSTER = 'booster'
    BADGE = 'badge'
    RANK = 'ranked'
    TITLE = 'title'
    RESERVE = 'reserve'
    BLUEPRINT = 'blueprints'
    SESSION_STATS = 'sessionStats'
    CREW_BOOK = 'crewBook'
    FESTIVAL = 'festival'


class ACTION_TOOLTIPS_TYPE(CONST_CONTAINER):
    ECONOMICS = 'economics'
    ITEM = 'item'
    BOOSTER = 'booster'
    CAMOUFLAGE = 'camouflage'
    EMBLEMS = 'emblems'
    AMMO = 'ammo'
    RENT = 'rent'


class ACTION_TOOLTIPS_STATE(CONST_CONTAINER):
    DISCOUNT = 'discount'
    PENALTY = 'penalty'


class ToolTipBaseData(object):

    def __init__(self, context, toolTipType):
        super(ToolTipBaseData, self).__init__()
        self._context = context
        self._toolTipType = toolTipType
        self.calledBy = None
        return

    @sf_lobby
    def app(self):
        return None

    @property
    def context(self):
        return self._context

    def isDynamic(self):
        return False

    def getDisplayableData(self, *args, **kwargs):
        return None

    def buildToolTip(self, *args, **kwargs):
        return {'type': self.getType(),
         'component': self.context.getComponent(),
         'data': self.getDisplayableData(*args, **kwargs)}

    def getType(self):
        return self._toolTipType


class ToolTipData(ToolTipBaseData):

    def __init__(self, context, toolTipType):
        super(ToolTipData, self).__init__(context, toolTipType)
        self.item = None
        self.fields = tuple()
        return

    def getDisplayableData(self, *args, **kwargs):
        self.item = self.context.buildItem(*args, **kwargs)
        result = dict()
        for field in self.fields:
            key, value = field.buildData()
            if field.isAvailable and key not in self.context.fieldsToExclude:
                result[key] = value

        return result


class ToolTipDataField(object):

    def __init__(self, tooltip, name):
        self._tooltip = weakref.proxy(tooltip)
        self._name = name
        self._isAvailable = True

    def buildData(self):
        return (self._name, self._getValue())

    @property
    def isAvailable(self):
        return self._isAvailable

    def _getValue(self):
        return None


class ToolTipAttrField(ToolTipDataField):

    def __init__(self, context, name, attr=None):
        super(ToolTipAttrField, self).__init__(context, name)
        self._attr = attr

    def _getItem(self):
        return self._tooltip.item

    def _getValue(self):
        attr = self._attr or self._name
        item = self._getItem()
        return getattr(item, attr) if hasattr(item, attr) else super(ToolTipAttrField, self)._getValue()


class ToolTipMethodField(ToolTipDataField):

    def __init__(self, context, name, method=None, args=None):
        super(ToolTipMethodField, self).__init__(context, name)
        self._method = method
        self._args = args or tuple()

    def _getItem(self):
        return self._tooltip.item

    def _getValue(self):
        attr = self._method or self._name
        item = self._getItem()
        return getattr(item, attr)(*self._args) if hasattr(item, attr) else super(ToolTipMethodField, self)._getValue()


class ToolTipAttrCheckField(ToolTipAttrField):

    def __init__(self, context, name, value, attr=None):
        super(ToolTipAttrCheckField, self).__init__(context, name, attr)
        self._value = value

    def _getValue(self):
        return super(ToolTipAttrCheckField, self)._getValue() == self._value


class ToolTipMethodCheckField(ToolTipMethodField):

    def __init__(self, context, name, value, method=None, args=None):
        super(ToolTipMethodCheckField, self).__init__(context, name, method, args)
        self._value = value

    def _getValue(self):
        return super(ToolTipMethodCheckField, self)._getValue() == self._value


class ToolTipParameterField(ToolTipDataField):

    def _getParameterValue(self, *args):
        return None


def getComplexStatus(statusKey, **kwargs):
    try:
        if not statusKey:
            return (None, None)
        headerKey = statusKey + '/header'
        textKey = statusKey + '/text'
        header = makeString(headerKey, **kwargs)
        text = makeString(textKey, **kwargs)
        if headerKey == TOOLTIPS.VEHICLESTATUS_INPREMIUMIGRONLY_HEADER:
            icon = icons.premiumIgrSmall()
            header = makeString(headerKey, icon=icon)
        if header == headerKey.split(':', 1)[1]:
            header = None
        if text == textKey.split(':', 1)[1]:
            text = None
        return (header, text)
    except Exception:
        LOG_CURRENT_EXCEPTION()
        return (None, None)

    return


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getUnlockPrice(compactDescr, parentCD=None, vehicleLevel=UNKNOWN_VEHICLE_LEVEL, itemsCache=None):
    itemTypeId, _, _ = vehicles.parseIntCompactDescr(compactDescr)
    freeXP = itemsCache.items.stats.actualFreeXP
    unlocks = itemsCache.items.stats.unlocks
    xpVehs = itemsCache.items.stats.vehiclesXPs
    g_techTreeDP.load()
    pricesDict = g_techTreeDP.getUnlockPrices(compactDescr)

    def getUnlockProps(isAvailable, vehCompDescr, unlockProps=None):
        unlockPrice = unlockProps.xpCost if unlockProps is not None else pricesDict.get(vehCompDescr, 0)
        oldPrice = unlockProps.xpFullCost if unlockProps is not None else unlockPrice
        discount = unlockProps.discount if unlockProps is not None else 0
        pVehXp = xpVehs.get(vehCompDescr, 0)
        need = unlockPrice - pVehXp
        needWithFreeXP = need - freeXP
        return (isAvailable,
         unlockPrice,
         min(need, needWithFreeXP),
         oldPrice,
         discount)

    if itemTypeId == vehicles._VEHICLE:
        isAvailable, unlockProps = g_techTreeDP.isNext2Unlock(compactDescr, unlocks, xpVehs, freeXP, vehicleLevel)
        if parentCD is not None and parentCD == unlockProps.parentID:
            return getUnlockProps(isAvailable, parentCD, unlockProps)
        xpCost = pricesDict.get(parentCD, 0)
        discount, newCost = g_techTreeDP.getBlueprintDiscountData(compactDescr, vehicleLevel, xpCost)
        unlockProps = UnlockProps(parentCD, -1, newCost, None, discount, xpCost)
        return getUnlockProps(isAvailable, unlockProps.parentID, unlockProps)
    else:
        isAvailable = compactDescr in unlocks
        if not pricesDict:
            return (isAvailable,
             0,
             0,
             0,
             0)
        if parentCD is not None:
            return getUnlockProps(isAvailable, parentCD)
        vehsCompDescrs = [ compDescr for compDescr in pricesDict.keys() if compDescr in unlocks ]
        if not vehsCompDescrs:
            vehsCompDescrs = pricesDict.keys()
        minUnlockPrice = sys.maxint
        minUnlockPriceVehCD = None
        for vcd in vehsCompDescrs:
            if pricesDict[vcd] <= minUnlockPrice:
                minUnlockPrice = pricesDict[vcd]
                minUnlockPriceVehCD = vcd

        if minUnlockPriceVehCD is None:
            return (isAvailable,
             0,
             0,
             0,
             0)
        return getUnlockProps(isAvailable, minUnlockPriceVehCD)
        return
