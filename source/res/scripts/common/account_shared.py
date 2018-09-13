# Embedded file name: scripts/common/account_shared.py
import time
import collections
from items import vehicles, ITEM_TYPES
from constants import IGR_TYPE
from debug_utils import *
import ArenaType
_ITEM_TYPE_GUN = ITEM_TYPES['vehicleGun']
_ITEM_TYPE_TURRET = ITEM_TYPES['vehicleTurret']

class AmmoIterator(object):

    def __init__(self, ammo):
        self.__ammo = ammo
        self.__idx = 0

    def __iter__(self):
        return self

    def next(self):
        if self.__idx >= len(self.__ammo):
            raise StopIteration
        idx = self.__idx
        self.__idx += 2
        return (abs(self.__ammo[idx]), self.__ammo[idx + 1])


class LayoutIterator(object):

    def __init__(self, layout):
        self.__layout = layout
        self.__idx = 0

    def __iter__(self):
        return self

    def next(self):
        if self.__idx >= len(self.__layout):
            raise StopIteration
        idx = self.__idx
        self.__idx += 2
        compDescr = self.__layout[idx]
        return (abs(compDescr), self.__layout[idx + 1], compDescr < 0)


def getAmmoDiff(ammo1, ammo2):
    diff = collections.defaultdict(int)
    for compDescr, count in AmmoIterator(ammo1):
        diff[abs(compDescr)] += count

    for compDescr, count in AmmoIterator(ammo2):
        diff[abs(compDescr)] -= count

    return diff


def getEquipmentsDiff(eqs1, eqs2):
    diff = collections.defaultdict(int)
    for eqCompDescr in eqs1:
        if eqCompDescr != 0:
            diff[abs(eqCompDescr)] += 1

    for eqCompDescr in eqs2:
        if eqCompDescr != 0:
            diff[abs(eqCompDescr)] -= 1

    return diff


def currentWeekPlayDaysCount(curTime, newDayStart, newWeekStart):
    curTime += newDayStart
    wday = time.gmtime(curTime).tm_wday + 1
    curWeekPlayDaysCnt = wday - newWeekStart
    if newWeekStart >= 0:
        if curWeekPlayDaysCnt == 0:
            curWeekPlayDaysCnt = 7
        elif curWeekPlayDaysCnt < 0:
            curWeekPlayDaysCnt += 7
    elif curWeekPlayDaysCnt == 8:
        curWeekPlayDaysCnt = 1
    elif curWeekPlayDaysCnt > 8:
        curWeekPlayDaysCnt -= 7
    return curWeekPlayDaysCnt


def getIGRCustomization(igrCustomizationsLayout, vehInvID, cutName, accountIGRType, position, defID):
    if cutName == 'camouflage':
        default = (None, vehicles._CUSTOMIZATION_EPOCH, 0)
    elif cutName == 'emblem':
        default = (defID, vehicles._CUSTOMIZATION_EPOCH, 0)
    elif cutName == 'inscription':
        default = (None,
         vehicles._CUSTOMIZATION_EPOCH,
         0,
         0)
    else:
        raise False or AssertionError
    vehInfo = igrCustomizationsLayout.get(vehInvID, None)
    if vehInfo is None:
        return default
    igrTypeInfo = vehInfo.get(accountIGRType, None)
    if igrTypeInfo is None:
        return default
    customInfo = igrTypeInfo.get(cutName, None)
    if customInfo is None:
        return default
    else:
        return customInfo.get(position, default)


def getIGRCustomizedVehCompDescr(igrCustomizationsLayout, vehInvID, accountIGRType, vehCompDescr):
    if accountIGRType == IGR_TYPE.NONE:
        return vehCompDescr
    else:
        vehDescr = vehicles.VehicleDescr(vehCompDescr)
        defID = vehDescr.type.defaultPlayerEmblemID
        for propName, positions in (('playerInscriptions', 4), ('playerEmblems', 4), ('camouflages', 3)):
            propValue = getattr(vehDescr, propName, None)
            if propValue is None:
                continue
            for pos in range(0, positions):
                if propName == 'playerEmblems':
                    data = getIGRCustomization(igrCustomizationsLayout, vehInvID, 'emblem', accountIGRType, pos, defID)
                    if data[0] != defID:
                        vehDescr.setPlayerEmblem(pos, *data)
                elif propName == 'playerInscriptions':
                    data = getIGRCustomization(igrCustomizationsLayout, vehInvID, 'inscription', accountIGRType, pos, None)
                    if data[0] is not None:
                        vehDescr.setPlayerInscription(pos, *data)
                elif propName == 'camouflages':
                    data = getIGRCustomization(igrCustomizationsLayout, vehInvID, 'camouflage', accountIGRType, pos, None)
                    if data[0] is not None:
                        vehDescr.setCamouflage(pos, *data)

        return vehDescr.makeCompactDescr()


def getHistoricalCustomization(igrCustomizationsLayout, vehInvID, accountIGRType, vehCompDescr, battleDef):

    def log(*args):
        pass

    vehTypeCompDescr = vehicles.getVehicleTypeCompactDescr(vehCompDescr)
    vehicleDef = battleDef['vehicles'].get(vehTypeCompDescr)
    if not vehicleDef:
        LOG_WARNING('No historical vehicle def for vehType=%s, battleID=%s' % (vehTypeCompDescr, battleDef['id']))
        return
    else:
        vehDescr = vehicles.VehicleDescr(compactDescr=vehCompDescr)
        vehDefModules = vehicleDef['modules'].copy()
        gunCompDescr = vehDefModules.pop(_ITEM_TYPE_GUN)
        turretCompDescr = vehDefModules.pop(_ITEM_TYPE_TURRET)
        for itemType, itemCompDescr in vehDefModules.iteritems():
            log('Changing component', vehTypeCompDescr, itemType, itemCompDescr)
            vehDescr.installComponent(itemCompDescr)

        log('Changing turret/gun', vehTypeCompDescr, turretCompDescr, gunCompDescr)
        vehDescr.installTurret(turretCompDescr, gunCompDescr)
        histCamouflageID = vehicleDef.get('camouflageID')
        arenaGeometryID = battleDef['arenaTypeID']
        camouflageSeasonKind = ArenaType.g_cache[arenaGeometryID].vehicleCamouflageKind
        currentCamouflageID = vehDescr.camouflages[camouflageSeasonKind][0]
        if currentCamouflageID is None:
            igrCamoData = getIGRCustomization(igrCustomizationsLayout, vehInvID, 'camouflage', accountIGRType, camouflageSeasonKind, 0)
            if igrCamoData[0] is not None:
                currentCamouflageID = igrCamoData[0]
                log('Igr camoID=%s [%s]' % (currentCamouflageID, camouflageSeasonKind))
        if currentCamouflageID is not None:
            log('Replacing camoID=%s [%s] with historical camoID=%s' % (currentCamouflageID, camouflageSeasonKind, histCamouflageID))
            vehDescr.setCamouflage(camouflageSeasonKind, histCamouflageID, time.time(), 1)
        else:
            log('No current camoID=%s [%s]' % (currentCamouflageID, camouflageSeasonKind))
        for position in xrange(0, 4):
            vehDescr.setPlayerEmblem(position, None, 0, 0)

        return vehDescr


def getCustomizedVehCompDescr(igrCustomizationsLayout, vehInvID, accountIGRType, vehCompDescr, historicalBattleDef = None):
    if historicalBattleDef is not None:
        vehDescr = getHistoricalCustomization(igrCustomizationsLayout, vehInvID, accountIGRType, vehCompDescr, historicalBattleDef)
        return vehDescr.makeCompactDescr()
    else:
        return getIGRCustomizedVehCompDescr(igrCustomizationsLayout, vehInvID, accountIGRType, vehCompDescr)
        return
