# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/custom/cache.py
import nations
from items import vehicles

def getCache():
    global _g_cache
    return _g_cache


def buildCache():
    vehiclesByLevel = {}
    vehiclesByTag = {'beast': set(),
     'sinai': set(),
     'patton': set()}
    vehiclesInTreeByNation = {}
    vehiclesInTree = set()
    nationsWithVehiclesInTree = []
    unlocksSources = vehicles.getUnlocksSources()
    for nationIdx in xrange(len(nations.NAMES)):
        nationList = vehicles.g_list.getList(nationIdx)
        vehiclesInNationTree = set()
        for vehDescr in nationList.itervalues():
            if 'bob' in vehDescr.tags:
                continue
            vehiclesByLevel.setdefault(vehDescr.level, set()).add(vehDescr.compactDescr)
            for tag in ('beast', 'sinai', 'patton'):
                if tag in vehDescr.tags:
                    vehiclesByTag[tag].add(vehDescr.compactDescr)

            if len(unlocksSources.get(vehDescr.compactDescr, set())) > 0 or len(vehicles.g_cache.vehicle(nationIdx, vehDescr.id).unlocksDescrs) > 0:
                vehiclesInNationTree.add(vehDescr.compactDescr)

        vehiclesInTree.update(vehiclesInNationTree)
        vehiclesInTreeByNation[nationIdx] = vehiclesInNationTree
        if bool(vehiclesInNationTree):
            nationsWithVehiclesInTree.append(nationIdx)

    vehicles8p = vehiclesByLevel[8] | vehiclesByLevel[9] | vehiclesByLevel[10]
    _g_cache.update({'vehiclesByLevel': vehiclesByLevel,
     'vehicles8+': vehicles8p,
     'vehiclesByTag': vehiclesByTag,
     'mausTypeCompDescr': vehicles.makeVehicleTypeCompDescrByName('germany:G42_Maus'),
     'vehiclesInTreesByNation': vehiclesInTreeByNation,
     'vehiclesInTrees': vehiclesInTree,
     'nationsWithVehiclesInTree': nationsWithVehiclesInTree})


_g_cache = {}
