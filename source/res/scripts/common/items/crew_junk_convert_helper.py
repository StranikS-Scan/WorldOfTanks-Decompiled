# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/crew_junk_convert_helper.py
from collections import defaultdict
import typing
from items import tankmen, vehicles
if typing.TYPE_CHECKING:
    from typing import Dict, List, Tuple
    from items.tankmen import TankmanDescr
XP_TRASH_LIMIT = 210060
VALID_GROUP = ('men1', 'women1')
NATIONS_CREW_BOOKS = {0: {'guideCD': 5406,
     'crewBookCD': 10526,
     'brochureCD': 286},
 1: {'guideCD': 5662,
     'crewBookCD': 10782,
     'brochureCD': 542},
 2: {'guideCD': 5918,
     'crewBookCD': 11038,
     'brochureCD': 798},
 3: {'guideCD': 7198,
     'crewBookCD': 12318,
     'brochureCD': 2078},
 4: {'guideCD': 6174,
     'crewBookCD': 11294,
     'brochureCD': 1054},
 5: {'guideCD': 6430,
     'crewBookCD': 11550,
     'brochureCD': 1310},
 6: {'guideCD': 6686,
     'crewBookCD': 11806,
     'brochureCD': 1566},
 7: {'guideCD': 6942,
     'crewBookCD': 12062,
     'brochureCD': 1822},
 8: {'guideCD': 7710,
     'crewBookCD': 12830,
     'brochureCD': 2590},
 9: {'guideCD': 7454,
     'crewBookCD': 12574,
     'brochureCD': 2334},
 10: {'guideCD': 7966,
      'crewBookCD': 13086,
      'brochureCD': 2846}}
CREW_BOOK_XP = 250001
GUIDE_XP = 100001
BROCHURE_XP = 20001

def findJunkTankmen(tankmenCompDescrs, vehicles=None):
    removeTankmenList = {}
    for key, compDescr in tankmenCompDescrs.iteritems():
        if vehicles is not None and key in vehicles:
            continue
        tankmanDescr = tankmen.TankmanDescr(compDescr)
        if isTrashTankman(tankmanDescr):
            removeTankmenList[key] = tankmanDescr

    return removeTankmenList


def calculateXpFromTankmen(tankmenCompDescrs):
    savingXPByNation = defaultdict(int)
    cashVehicleNativeType = {}
    for tankmanDescr in tankmenCompDescrs:
        _savingTrashTankmanXP(tankmanDescr, cashVehicleNativeType, savingXPByNation)

    return savingXPByNation


def getNationBooksFromXp(xpByNation):
    crewBooks = {}
    for nationID, xp in xpByNation.iteritems():
        if not xp:
            continue
        crewBookCD = NATIONS_CREW_BOOKS[nationID]['crewBookCD']
        guideCD = NATIONS_CREW_BOOKS[nationID]['guideCD']
        brochureCD = NATIONS_CREW_BOOKS[nationID]['brochureCD']
        itemCount = xp // CREW_BOOK_XP
        xp %= CREW_BOOK_XP
        if itemCount > 0:
            crewBooks[crewBookCD] = crewBooks.get(crewBookCD, 0) + itemCount
        itemCount = xp // GUIDE_XP
        xp %= GUIDE_XP
        if itemCount > 0:
            crewBooks[guideCD] = crewBooks.get(guideCD, 0) + itemCount
        itemCount = xp // BROCHURE_XP + 1
        crewBooks[brochureCD] = crewBooks.get(brochureCD, 0) + itemCount

    return crewBooks


def _savingTrashTankmanXP(tankmanDescr, cashVehicleNativeType, savingXPByNation):
    nationID = tankmanDescr.nationID
    typeID = (nationID, tankmanDescr.vehicleTypeID)
    if typeID in cashVehicleNativeType:
        vehType = cashVehicleNativeType[typeID]
    else:
        vehicleNativeDescr = vehicles.VehicleDescr(typeID=typeID)
        vehType = vehicles.getVehicleType(vehicleNativeDescr.type.compactDescr)
        cashVehicleNativeType[typeID] = vehType
    xp = tankmanDescr.totalXP()
    if xp > 0:
        savingXPByNation[nationID] += xp / len(vehType.crewRoles)


def isTrashTankman(tankman):
    if checkXPLimit(tankman):
        return False
    if checkUnique(tankman):
        return False
    return False if not checkFreeSkills(tankman) else True


def checkXPLimit(tankman):
    tankmanXP = tankman.totalXP()
    return tankmanXP >= XP_TRASH_LIMIT


def checkFreeSkills(tankman):
    return False if tankman.freeSkillsNumber > 0 else True


def checkUnique(tankman):
    nationConfig = tankmen.getNationConfig(tankman.nationID)
    group = nationConfig.getGroups(tankman.isPremium)[tankman.gid]
    return group.name not in VALID_GROUP
