# Embedded file name: scripts/common/fortified_regions.py
import ResMgr
import ArenaType
from debug_utils import *
_CONFIG_FILE = 'scripts/item_defs/fortified_regions.xml'
from constants import FORT_BUILDING_TYPE, FORT_ORDER_TYPE

def _getInt(section, name, default = 0):
    field = section[name]
    if field is None:
        return default
    else:
        return field.asInt


def _getString(section, name, default = ''):
    field = section[name]
    if field is None:
        return default
    else:
        return field.asString


class BuildingType:

    def __init__(self, type, name, section):
        self.type = type
        self.name = name
        self.levels = {}
        self.attachedPlayersLimit = _getInt(section, 'attached_players_limit', 0)
        orderName = _getString(section, 'order')
        self.orderType = orderType = getattr(FORT_ORDER_TYPE, orderName, None)
        if orderName and not orderType:
            raise Exception, 'Unknown order name (%s)' % (orderName,)
        self.levels = levels = {}
        levelsSection = section['levels'] or {}
        for name, subsection in levelsSection.items():
            level = subsection.asInt
            levels[level] = BuildingTypeLevel(subsection)

        return

    def __repr__(self):
        return 'BuildingType(\n type=%s, name=%s, attachedPlayersLimit=%s, orderType=%s\n levels=%s' % (self.type,
         self.name,
         self.attachedPlayersLimit,
         self.orderType,
         self.levels)


class BuildingTypeLevel:

    def __init__(self, subsection):
        self.hp = subsection['hp'].asInt
        self.storage = subsection['storage'].asInt
        self.upgradeCost = _getInt(subsection, 'upgrade_cost', 0)
        self.maxOrdersCount = _getInt(subsection, 'max_orders_count', 0)

    def __repr__(self):
        return 'BuildingTypeLevel( hp=%s, storage=%s, upgradeCost=%s, maxOrdersCount=%s' % (self.hp,
         self.storage,
         self.upgradeCost,
         self.maxOrdersCount)


class OrderType:

    def __init__(self, type, name, section):
        self.type = type
        self.name = name
        self.levels = levels = {}
        levelsSection = section['levels'] or {}
        for name, subsection in levelsSection.items():
            level = subsection.asInt
            levels[level] = orderLevel = OrderTypeLevel(subsection)


class OrderTypeLevel:

    def __init__(self, subsection):
        self.effectValue = subsection['effect_value'].asInt
        self.effectTime = _getInt(subsection, 'effect_time', 0)
        self.productionCost = subsection['production_cost'].asInt
        self.productionTime = subsection['production_time'].asInt


class TransportLevel:

    def __init__(self, subsection):
        self.maxResource = subsection['max_resource'].asInt
        self.cooldownTime = subsection['cooldown_time'].asInt


class DefenceConditions:

    def __init__(self, subsection):
        self.minRegionLevel = subsection['min_region_level'].asInt
        self.minDirections = subsection['min_directions'].asInt
        self.minClanMembers = subsection['min_clan_members'].asInt


class Division:

    def __init__(self, subsection):
        self.minPoints = subsection['min_points'].asInt
        self.maxPoints = subsection['max_points'].asInt
        self.resourceBonus = subsection['resource_bonus'].asInt
        self.maps = set(subsection['maps'].asString.split())


class FortifiedRegionCache:

    def __init__(self):
        self.isSupported = False
        self.clanMembersForStart = 0
        self.startResource = 0
        self.maxDirections = 0
        self.clanMembersPerDirection = 0
        self.isFirstDirectionFree = False
        self.defenseHourPreorderTime = 0
        self.defenseHourCooldownTime = 0
        self.offdayPreorderTime = 0
        self.offdayCooldownTime = 0
        self.minVacationPreorderTime = 0
        self.maxVacationPreorderTime = 0
        self.minVacationDuration = 0
        self.maxVacationDuration = 0
        self.vacationCooldownTime = 0
        self.allowSortieLegionaries = False
        self.maxLegionariesCount = 0
        self.buildings = {}
        self.orders = {}
        self.transportLevels = {}
        self.defenceConditions = None
        self.divisions = {}
        return


g_cache = None

def init():
    global g_cache
    LOG_NOTE('fortified_regions.init()')
    g_cache = FortifiedRegionCache()
    section = ResMgr.openSection(_CONFIG_FILE)
    g_cache.isSupported = section['is_supported'].asBool
    g_cache.clanMembersForStart = section['clan_members_for_start'].asInt
    g_cache.startResource = section['start_resource'].asInt
    g_cache.maxDirections = section['max_directions'].asInt
    g_cache.clanMembersPerDirection = section['clan_members_per_direction'].asInt
    g_cache.isFirstDirectionFree = section['is_first_direction_free'].asBool
    g_cache.defenseHourPreorderTime = section['defense_hour_preorder_time'].asInt
    g_cache.defenseHourCooldownTime = section['defense_hour_cooldown_time'].asInt
    g_cache.offdayPreorderTime = section['offday_preorder_time'].asInt
    g_cache.offdayCooldownTime = section['offday_cooldown_time'].asInt
    g_cache.minVacationPreorderTime = section['min_vacation_preorder_time'].asInt
    g_cache.maxVacationPreorderTime = section['max_vacation_preorder_time'].asInt
    g_cache.vacationCooldownTime = section['vacation_cooldown_time'].asInt
    g_cache.minVacationDuration = section['min_vacation_duration'].asInt
    g_cache.maxVacationDuration = section['max_vacation_duration'].asInt
    g_cache.maxSorties = section['max_sorties'].asInt
    g_cache.allowSortieLegionaries = section['allow_sortie_legionaries'].asBool
    g_cache.maxLegionariesCount = section['max_legionaries_count'].asInt
    g_cache.transportLevels = transportLevels = {}
    transportLevelsSection = section['transport_levels'] or {}
    for name, subsection in transportLevelsSection.items():
        level = subsection.asInt
        transportLevels[level] = TransportLevel(subsection)

    subsection = section['defence_conditions']
    g_cache.defenceConditions = defenceConditions = DefenceConditions(subsection)
    g_cache.divisions = divisions = {}
    for name, subsection in section['divisions'].items():
        divisions[name] = Division(subsection)

    g_cache.buildings = buildings = {}
    for buildName, subsection in section['buildings'].items():
        buildTypeID = getattr(FORT_BUILDING_TYPE, buildName, None)
        if not buildTypeID:
            raise Exception, 'Unknown building name (%s)' % (buildName,)
        if buildTypeID in buildings:
            raise Exception, 'Duplicate building type (%s)' % (buildTypeID,)
        buildings[buildTypeID] = BuildingType(buildTypeID, buildName, subsection)

    g_cache.orders = orders = {}
    for orderName, subsection in section['orders'].items():
        orderTypeID = getattr(FORT_ORDER_TYPE, orderName, None)
        if not orderTypeID:
            raise Exception, 'Unknown order name (%s)' % (orderName,)
        if orderTypeID in orders:
            raise Exception, 'Duplicate order type (%s)' % (orderTypeID,)
        orders[orderTypeID] = OrderType(orderTypeID, orderName, subsection)

    return
