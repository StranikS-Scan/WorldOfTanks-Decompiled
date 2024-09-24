# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/custom/cache.py
import nations
from items import vehicles, parseIntCompactDescr
from collector_vehicle import CollectorVehicleConsts
PRESTIGE_ALLOWED_TAGS = {'role_ATSPG_sniper',
 'role_ATSPG_universal',
 'role_ATSPG_support',
 'role_LT_universal',
 'role_LT_wheeled',
 'role_SPG',
 'role_HT_break',
 'role_HT_universal',
 'role_HT_support',
 'role_MT_assault',
 'role_MT_universal',
 'role_MT_sniper',
 'role_MT_support',
 'role_ATSPG_assault',
 'role_HT_assault',
 'special',
 'collectorVehicle',
 'secret',
 'testTank',
 'private',
 'event_battles',
 'fallout',
 'epic_battles',
 'mapbox',
 'fun_random',
 'rent_promotion',
 'premiumIGR',
 'pillbox',
 'fr_hidden',
 'mode_hidden',
 'disableIBA',
 'comp7',
 'bot_hunter',
 'clanWarsBattles'}
EXCLUDE_VEHICLE_BY_TAGS = {'bob',
 'battle_royale',
 'maps_training',
 'bunkerTurret',
 'event_battles'}

def getCache():
    global _g_cache
    return _g_cache


def buildCache():
    vehiclesByLevel = {}
    TAGS_TO_COLLECT = {'beast', 'sinai', 'patton'}.union(PRESTIGE_ALLOWED_TAGS)
    vehiclesByTag = {tag:set() for tag in TAGS_TO_COLLECT}
    vehiclesInTreeByNation = {}
    vehiclesInTree = set()
    nationsWithVehiclesInTree = []
    collectorVehiclesByNations = {}
    collectorVehiclesLevelsByNations = {}
    vehiclesNameToDescr = {}
    vehicleEliteStatusXp = {}
    vehiclesByClass = {tag:set() for tag in vehicles.VEHICLE_CLASS_TAGS}
    unlocksSources = vehicles.getUnlocksSources()
    for nationIdx in xrange(len(nations.NAMES)):
        nationList = vehicles.g_list.getList(nationIdx)
        vehiclesInNationTree = set()
        for vehDescr in nationList.itervalues():
            if EXCLUDE_VEHICLE_BY_TAGS.intersection(vehDescr.tags):
                continue
            vehiclesNameToDescr[vehDescr.name] = vehDescr.compactDescr
            vehicleEliteStatusXp[vehDescr.compactDescr] = __getVehicleEliteStatusXp(vehDescr.compactDescr)
            vehiclesByLevel.setdefault(vehDescr.level, set()).add(vehDescr.compactDescr)
            for tag in TAGS_TO_COLLECT:
                if tag in vehDescr.tags:
                    vehiclesByTag[tag].add(vehDescr.compactDescr)

            for tag in vehicles.VEHICLE_CLASS_TAGS:
                if tag in vehDescr.tags:
                    vehiclesByClass[tag].add(vehDescr.compactDescr)

            if CollectorVehicleConsts.COLLECTOR_VEHICLES_TAG in vehDescr.tags:
                collectorVehiclesByNations.setdefault(nationIdx, set()).add(vehDescr.compactDescr)
                collectorVehiclesLevelsByNations.setdefault(nationIdx, set()).add(vehDescr.level)
                continue
            if len(unlocksSources.get(vehDescr.compactDescr, set())) > 0 or len(vehicles.g_cache.vehicle(nationIdx, vehDescr.id).unlocksDescrs) > 0:
                vehiclesInNationTree.add(vehDescr.compactDescr)

        vehiclesInTree.update(vehiclesInNationTree)
        vehiclesInTreeByNation[nationIdx] = vehiclesInNationTree
        if bool(vehiclesInNationTree):
            nationsWithVehiclesInTree.append(nationIdx)

    vehicles8p = vehiclesByLevel[8] | vehiclesByLevel[9] | vehiclesByLevel[10]
    _g_cache.update({'vehiclesByLevel': vehiclesByLevel,
     'vehicles8+': vehicles8p,
     'vehiclesInTreesWithout1Lvl': vehiclesInTree - vehiclesByLevel[1],
     'vehiclesByTag': vehiclesByTag,
     'mausTypeCompDescr': vehicles.makeVehicleTypeCompDescrByName('germany:G42_Maus'),
     'vehiclesInTreesByNation': vehiclesInTreeByNation,
     'vehiclesInTrees': vehiclesInTree,
     'nationsWithVehiclesInTree': nationsWithVehiclesInTree,
     'collectorVehiclesByNations': collectorVehiclesByNations,
     'collectorVehiclesLevelsByNations': collectorVehiclesLevelsByNations,
     'vehiclesNameToDescr': vehiclesNameToDescr,
     'vehicleEliteStatusXp': vehicleEliteStatusXp,
     'vehiclesByClass': vehiclesByClass})


_g_cache = {}

def __getVehicleEliteStatusXp(vehicleCompDescr):
    eliteXpCost = 0
    vehType = vehicles.getVehicleType(vehicleCompDescr)
    for unlockDescr in vehType.unlocksDescrs:
        eliteXpCost += unlockDescr[0]

    return eliteXpCost
