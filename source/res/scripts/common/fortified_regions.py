# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/fortified_regions.py
import ResMgr
import ArenaType
from debug_utils import *
from constants import FORT_BUILDING_TYPE, FORT_ORDER_TYPE
from items import vehicles
_CONFIG_FILE = 'scripts/item_defs/fortified_regions.xml'

def _getInt(section, name, default=0):
    field = section[name]
    return default if field is None else field.asInt


def _getString(section, name, default=''):
    field = section[name]
    return default if field is None else field.asString


class BuildingType(object):
    __slots__ = ('type', 'name', 'levels', 'attachedPlayersLimit', 'orderType')

    def __init__(self, type, name, section):
        self.type = type
        self.name = name
        self.levels = levels = {}
        self.attachedPlayersLimit = _getInt(section, 'attached_players_limit')
        orderName = _getString(section, 'order')
        self.orderType = orderType = getattr(FORT_ORDER_TYPE, orderName, None)
        if orderName and not orderType:
            raise Exception('Unknown order name (%s)' % (orderName,))
        levelsSection = section['levels'] or {}
        for name, subsection in levelsSection.items():
            level = subsection.asInt
            levels[level] = BuildingTypeLevel(subsection)

        return

    def __repr__(self):
        return 'BuildingType(\n type=%s, name=%s, attachedPlayersLimit=%s, orderType=%s\n levels=%s)' % (self.type,
         self.name,
         self.attachedPlayersLimit,
         self.orderType,
         self.levels)


class BuildingTypeLevel(object):
    __slots__ = ('hp', 'storage', 'upgradeCost', 'maxOrdersCount')

    def __init__(self, subsection):
        self.hp = subsection['hp'].asInt
        self.storage = subsection['storage'].asInt
        self.upgradeCost = _getInt(subsection, 'upgrade_cost')
        self.maxOrdersCount = _getInt(subsection, 'max_orders_count')

    def __repr__(self):
        return 'BuildingTypeLevel( hp=%s, storage=%s, upgradeCost=%s, maxOrdersCount=%s)' % (self.hp,
         self.storage,
         self.upgradeCost,
         self.maxOrdersCount)


class OrderType(object):
    __slots__ = ('type', 'name', 'levels')

    def __init__(self, type, name, section):
        self.type = type
        self.name = name
        self.levels = levels = {}
        levelsSection = section['levels'] or {}
        for name, subsection in levelsSection.items():
            level = subsection.asInt
            levels[level] = OrderTypeLevel(subsection)


class OrderTypeLevel(object):
    __slots__ = ('effectValue', 'effectTime', 'productionCost', 'productionTime', 'equipment')

    def __init__(self, subsection):
        self.effectValue = subsection['effect_value'].asInt
        self.effectTime = _getInt(subsection, 'effect_time')
        self.productionCost = subsection['production_cost'].asInt
        self.productionTime = subsection['production_time'].asInt
        equipmentName = _getString(subsection, 'equipment', None)
        if not equipmentName:
            self.equipment = None
        else:
            cache = vehicles.g_cache
            equipmentIDs = cache.equipmentIDs()
            equipments = cache.equipments()
            eqID = equipmentIDs.get(equipmentName)
            if eqID is None:
                raise Exception("Unknown equipment '%s'" % equipmentName)
            self.equipment = equipments[eqID].compactDescr
        return


class TransportLevel(object):
    __slots__ = ('maxResource', 'cooldownTime')

    def __init__(self, subsection):
        self.maxResource = subsection['max_resource'].asInt
        self.cooldownTime = subsection['cooldown_time'].asInt


class DefenceConditions(object):
    __slots__ = ('minRegionLevel', 'minDirections', 'minClanMembers')

    def __init__(self, subsection):
        self.minRegionLevel = subsection['min_region_level'].asInt
        self.minDirections = subsection['min_directions'].asInt
        self.minClanMembers = subsection['min_clan_members'].asInt


class SortieDivision(object):
    __slots__ = ('isConsumables', 'minPoints', 'maxPoints', 'resourceBonus', 'influencePoints', 'maps')

    def __init__(self, subsection):
        self.isConsumables = subsection['is_consumables'].asBool
        self.minPoints = subsection['min_points'].asInt
        self.maxPoints = subsection['max_points'].asInt
        self.resourceBonus = subsection['resource_bonus'].asInt
        self.influencePoints = subsection['influence_points'].asInt
        self.maps = set(subsection['maps'].asString.split())


class FortDivision(object):
    __slots__ = ('isConsumables',)

    def __init__(self, subsection):
        self.isConsumables = subsection['is_consumables'].asBool


class FortifiedRegionCache(object):
    __slots__ = ('isSupported', 'clanMembersForStart', 'startResource', 'maxDirections', 'clanMembersPerDirection', 'defenseHourPreorderTime', 'defenseHourCooldownTime', 'defenseHourShutdownTime', 'offdayPreorderTime', 'offdayCooldownTime', 'minVacationPreorderTime', 'maxVacationPreorderTime', 'minVacationDuration', 'maxVacationDuration', 'vacationCooldownTime', 'vacationCooldownTime', 'allowSortieLegionaries', 'maxLegionariesCount', 'battleConsumablesCount', 'buildings', 'orders', 'orderTypeIDToBuildTypeID', 'transportLevels', 'defenceConditions', 'divisions', 'fort_divisions', 'fortBattleMaps', 'isFirstDirectionFree', 'openDirAttacksTime', 'attackCooldownTime', 'attackPreorderTime', 'attackMaxTime', 'mapCooldownTime', 'changePeripheryCooldownTime', 'maxSorties', 'consumablesSlotCount', 'maxLifetimeConsumable', 'bonusFactors', 'equipmentToOrder', 'fortInfluencePointsFactors')

    def __init__(self):
        self.isSupported = False
        self.clanMembersForStart = 0
        self.startResource = 0
        self.maxDirections = 0
        self.clanMembersPerDirection = 0
        self.isFirstDirectionFree = False
        self.openDirAttacksTime = 0
        self.attackCooldownTime = 0
        self.attackPreorderTime = 0
        self.attackMaxTime = 0
        self.defenseHourPreorderTime = 0
        self.defenseHourCooldownTime = 0
        self.defenseHourShutdownTime = 0
        self.offdayPreorderTime = 0
        self.offdayCooldownTime = 0
        self.minVacationPreorderTime = 0
        self.maxVacationPreorderTime = 0
        self.minVacationDuration = 0
        self.maxVacationDuration = 0
        self.vacationCooldownTime = 0
        self.allowSortieLegionaries = False
        self.maxLegionariesCount = 0
        self.battleConsumablesCount = 0
        self.mapCooldownTime = 0
        self.changePeripheryCooldownTime = 0
        self.maxSorties = 0
        self.consumablesSlotCount = 0
        self.maxLifetimeConsumable = 0
        self.buildings = {}
        self.orders = {}
        self.orderTypeIDToBuildTypeID = {}
        self.transportLevels = {}
        self.defenceConditions = None
        self.divisions = {}
        self.fort_divisions = {}
        self.fortBattleMaps = set()
        self.bonusFactors = {}
        self.equipmentToOrder = {}
        self.fortInfluencePointsFactors = {}
        return


g_cache = None

def init():
    global g_cache
    LOG_DEBUG('fortified_regions.init()')
    geometryNamesToIDs = dict([ (arenaType.geometryName, arenaType.geometryID) for arenaType in ArenaType.g_cache.itervalues() if not arenaType.explicitRequestOnly ])
    g_cache = FortifiedRegionCache()
    section = ResMgr.openSection(_CONFIG_FILE)
    g_cache.isSupported = section['is_supported'].asBool
    g_cache.clanMembersForStart = section['clan_members_for_start'].asInt
    g_cache.startResource = section['start_resource'].asInt
    g_cache.maxDirections = section['max_directions'].asInt
    g_cache.clanMembersPerDirection = section['clan_members_per_direction'].asInt
    g_cache.isFirstDirectionFree = section['is_first_direction_free'].asBool
    g_cache.openDirAttacksTime = section['open_dir_attacks_time'].asInt
    g_cache.attackCooldownTime = section['attack_cooldown_time'].asInt
    g_cache.attackPreorderTime = section['attack_preorder_time'].asInt
    g_cache.attackMaxTime = section['attack_max_time'].asInt
    g_cache.defenseHourPreorderTime = section['defense_hour_preorder_time'].asInt
    g_cache.defenseHourCooldownTime = section['defense_hour_cooldown_time'].asInt
    g_cache.defenseHourShutdownTime = section['defense_hour_shutdown_time'].asInt
    g_cache.changePeripheryCooldownTime = section['change_periphery_cooldown_time'].asInt
    g_cache.offdayPreorderTime = section['offday_preorder_time'].asInt
    g_cache.offdayCooldownTime = section['offday_cooldown_time'].asInt
    g_cache.minVacationPreorderTime = section['min_vacation_preorder_time'].asInt
    g_cache.maxVacationPreorderTime = section['max_vacation_preorder_time'].asInt
    g_cache.vacationCooldownTime = section['vacation_cooldown_time'].asInt
    g_cache.minVacationDuration = section['min_vacation_duration'].asInt
    g_cache.maxVacationDuration = section['max_vacation_duration'].asInt
    g_cache.mapCooldownTime = section['map_cooldown_time'].asInt
    g_cache.maxSorties = section['max_sorties'].asInt
    g_cache.allowSortieLegionaries = section['allow_sortie_legionaries'].asBool
    g_cache.maxLegionariesCount = section['max_legionaries_count'].asInt
    g_cache.consumablesSlotCount = section['consumables_slot_count'].asInt
    g_cache.maxLifetimeConsumable = section['max_lifetime_consumable'].asInt
    g_cache.transportLevels = transportLevels = {}
    transportLevelsSection = section['transport_levels'] or {}
    for name, subsection in transportLevelsSection.items():
        level = subsection.asInt
        transportLevels[level] = TransportLevel(subsection)

    subsection = section['defence_conditions']
    g_cache.defenceConditions = DefenceConditions(subsection)
    g_cache.divisions = divisions = {}
    for name, subsection in section['divisions']['sortie'].items():
        divisions[name] = SortieDivision(subsection)

    g_cache.fort_divisions = fort_divisions = {}
    for name, subsection in section['divisions']['fort_battle'].items():
        fort_divisions[name] = FortDivision(subsection)

    for name in _getString(section, 'fort_battle_maps').split():
        if name not in geometryNamesToIDs:
            raise Exception('Unknown fort battle map name (%s)' % (name,))
        if geometryNamesToIDs[name] == 0:
            raise Exception('Zero geometryID is detected for battle map name %s' % (name,))
        g_cache.fortBattleMaps.add(geometryNamesToIDs[name])

    g_cache.buildings = buildings = {}
    g_cache.orderTypeIDToBuildTypeID = orderTypeIDToBuildTypeID = {}
    for buildName, subsection in section['buildings'].items():
        buildTypeID = getattr(FORT_BUILDING_TYPE, buildName, None)
        if not buildTypeID:
            raise Exception('Unknown building name (%s)' % (buildName,))
        if buildTypeID in buildings:
            raise Exception('Duplicate building type (%s)' % (buildTypeID,))
        buildings[buildTypeID] = buildingType = BuildingType(buildTypeID, buildName, subsection)
        orderTypeIDToBuildTypeID[buildingType.orderType] = buildTypeID

    g_cache.orders = orders = {}
    for orderName, subsection in section['orders'].items():
        orderTypeID = getattr(FORT_ORDER_TYPE, orderName, None)
        if not orderTypeID:
            raise Exception('Unknown order name (%s)' % (orderName,))
        if orderTypeID in orders:
            raise Exception('Duplicate order type (%s)' % (orderTypeID,))
        orders[orderTypeID] = OrderType(orderTypeID, orderName, subsection)

    g_cache.equipmentToOrder = equipmentToOrder = {}
    for orderTypeID, orderType in orders.items():
        for level, order in orderType.levels.items():
            equipment = order.equipment
            if equipment:
                if equipmentToOrder.get(equipment) is not None:
                    raise Exception('Duplicate order equipment (%s)' % (equipment,))
                equipmentToOrder[equipment] = (orderTypeID, level)

    g_cache.bonusFactors = factors = {}
    for name, subsection in section['fort_bonus_factors'].items():
        level = subsection.asInt
        factors.setdefault(level, {})
        for bonusName, bonusSubsection in subsection.items():
            if bonusName not in ('tankmenXP', 'tankmenXPFactor', 'xp', 'credits', 'freeXP', 'premium', 'gold', 'items'):
                raise Exception('Unsupported fort bonus factor (%s)' % (bonusName,))
            factors[level][bonusName] = bonusSubsection.asFloat

    if len(factors) != len(buildings[FORT_BUILDING_TYPE.OFFICE].levels):
        raise Exception('Number of levels in fort_bonus_factors must be equal to number of OFFICE levels')
    g_cache.fortInfluencePointsFactors = fortInfluencePointsFactors = {}
    for division, subsection in section['fortSortiesProfitRate'].items():
        fortInfluencePointsFactors[division] = subsection['fortInfluencePointsFactor'].asFloat

    return
