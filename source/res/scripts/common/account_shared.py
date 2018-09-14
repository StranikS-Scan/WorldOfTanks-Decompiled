# Embedded file name: scripts/common/account_shared.py
import time
import nations
import collections
from items import vehicles, ITEM_TYPES
from constants import IGR_TYPE, FAIRPLAY_VIOLATIONS_NAMES, FAIRPLAY_VIOLATIONS_MASKS
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


def getCustomizedComponentInIGR(igrCustomizationLayout, vehInvID, custType, accountIGRType, position, defID):
    if custType == 'camouflages':
        default = (None, vehicles._CUSTOMIZATION_EPOCH, 0)
    elif custType == 'emblems':
        default = (defID, vehicles._CUSTOMIZATION_EPOCH, 0)
    elif custType == 'inscriptions':
        default = (None,
         vehicles._CUSTOMIZATION_EPOCH,
         0,
         0)
    else:
        raise False or AssertionError
    vehInfo = igrCustomizationLayout.get(vehInvID, None)
    if vehInfo is None:
        return default
    igrTypeInfo = vehInfo.get(accountIGRType, None)
    if igrTypeInfo is None:
        return default
    customInfo = igrTypeInfo.get(custType, None)
    if customInfo is None:
        return default
    else:
        return customInfo.get(position, default)


def getIGRCustomizedVehCompDescr(igrCustomizationLayout, vehInvID, accountIGRType, vehCompDescr):
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
                    data = getCustomizedComponentInIGR(igrCustomizationLayout, vehInvID, 'emblems', accountIGRType, pos, defID)
                    if data[0] != defID:
                        vehDescr.setPlayerEmblem(pos, *data)
                elif propName == 'playerInscriptions':
                    data = getCustomizedComponentInIGR(igrCustomizationLayout, vehInvID, 'inscriptions', accountIGRType, pos, None)
                    if data[0] is not None:
                        vehDescr.setPlayerInscription(pos, *data)
                elif propName == 'camouflages':
                    data = getCustomizedComponentInIGR(igrCustomizationLayout, vehInvID, 'camouflages', accountIGRType, pos, None)
                    if data[0] is not None:
                        vehDescr.setCamouflage(pos, *data)

        return vehDescr.makeCompactDescr()


def getHistoricalCustomizedVehCompDescr(igrLayout, vehInvID, accountIGRType, vehCompDescr, battleDef):
    vehDescr = vehicles.VehicleDescr(vehCompDescr)
    vehicleDef = battleDef['vehicles'][vehDescr.type.compactDescr]
    histVehDescr = vehicles.VehicleDescr(vehicleDef['historicalVehCompDescr'])
    histCamouflageID = vehicleDef.get('camouflageID')
    arenaGeometryID = battleDef['arenaTypeID']
    camouflageSeasonKind = ArenaType.g_cache[arenaGeometryID].vehicleCamouflageKind
    currentCamouflageID = None
    if accountIGRType != IGR_TYPE.NONE:
        currentCamouflageID = getCustomizedComponentInIGR(igrLayout, vehInvID, 'camouflages', accountIGRType, camouflageSeasonKind, 0)[0]
    if currentCamouflageID is None:
        currentCamouflageID = vehDescr.camouflages[camouflageSeasonKind][0]
    if currentCamouflageID is not None and histCamouflageID is not None:
        histVehDescr.setCamouflage(camouflageSeasonKind, histCamouflageID, int(time.time()), 0)
    optionalDevices = vehDescr.optionalDevices
    for slotIdx in xrange(len(optionalDevices)):
        optDevice = optionalDevices[slotIdx]
        if optDevice is None:
            continue
        histVehDescr.installOptionalDevice(optDevice['compactDescr'], slotIdx)

    return histVehDescr


def getCustomizedVehCompDescr(igrLayout, vehInvID, accountIGRType, vehCompDescr, battleDef):
    if battleDef is not None:
        histVehDescr = getHistoricalCustomizedVehCompDescr(igrLayout, vehInvID, accountIGRType, vehCompDescr, battleDef)
        return histVehDescr.makeCompactDescr()
    else:
        return getIGRCustomizedVehCompDescr(igrLayout, vehInvID, accountIGRType, vehCompDescr)


def getFairPlayViolationName(violationsMask):
    if violationsMask == 0:
        return None
    else:
        for name in FAIRPLAY_VIOLATIONS_NAMES:
            if violationsMask & FAIRPLAY_VIOLATIONS_MASKS[name] != 0:
                return name

        return None


def getCamouflageIGRType(nationID, camouflageID):
    if camouflageID is None:
        return IGR_TYPE.NONE
    else:
        descr = vehicles.g_cache.customization(nationID)['camouflages'].get(camouflageID)
        if descr is None:
            raise Exception, 'Wrong camouflage idx'
        return descr['igrType']


def getPlayerInscriptionIGRType(nationID, inscriptionID):
    if inscriptionID is None:
        return IGR_TYPE.NONE
    else:
        customizationCache = vehicles.g_cache.customization(nationID)
        descr = customizationCache['inscriptions'].get(inscriptionID)
        if descr is None:
            raise Exception, 'Wrong inscription id'
        return descr[1]


def getPlayerEmblemIGRType(emblemID):
    if emblemID is None:
        return IGR_TYPE.NONE
    else:
        descr = vehicles.g_cache.playerEmblems()[1].get(emblemID)
        if descr is None:
            raise Exception, 'Wrong emblem idx'
        return descr[1]


def validateCustomizationItem(custData):
    custID = custData.get('id', None)
    custType = custData.get('custType', None)
    value = custData.get('value', None)
    isPermanent = custData.get('isPermanent', None)
    vehTypeCompDescr = custData.get('vehTypeCompDescr', None)
    if custID is None:
        return (False, 'Cust id is not specified')
    elif value is None or value == 0 or isPermanent is None:
        return (False, 'Invalid args')
    elif custType not in ('emblems', 'camouflages', 'inscriptions'):
        return (False, 'Invalid customization type')
    else:
        if custType == 'emblems':
            nationID = 0
            innationID = custID
        else:
            nationID, innationID = custID
        if nationID >= len(nations.AVAILABLE_NAMES) or nationID < 0:
            return (False, 'Invalid customization nation')
        if vehTypeCompDescr is not None:
            itemTypeID, vehNationID, vehInnationID = vehicles.parseIntCompactDescr(vehTypeCompDescr)
            if itemTypeID != ITEM_TYPES.vehicle:
                return (False, 'Invalid type compact descriptor')
            try:
                vehDescr = vehicles.VehicleDescr(typeID=(vehNationID, vehInnationID))
            except:
                LOG_CURRENT_EXCEPTION()
                return (False, 'Invalid type compact descriptor')

            if custType == 'camouflages':
                if nationID != vehDescr.type.customizationNationID:
                    return (False, 'Camouflage and vehTypeCompDescr mismatch')
                try:
                    vehDescr.setCamouflage(None, innationID, time.time(), 0)
                except:
                    LOG_CURRENT_EXCEPTION()
                    return (False, 'Camouflage and vehTypeCompDescr mismatch')

            elif custType == 'inscriptions':
                if nationID != vehDescr.type.customizationNationID:
                    return (False, 'Inscription and vehTypeCompDescr mismatch')
                try:
                    vehDescr.setPlayerInscription(0, innationID, time.time(), 0, 0)
                except:
                    LOG_CURRENT_EXCEPTION()
                    return (False, 'Inscription and vehTypeCompDescr mismatch')

            elif custType == 'emblems':
                try:
                    vehDescr.setPlayerEmblem(0, innationID, time.time(), 0)
                except:
                    LOG_CURRENT_EXCEPTION()
                    return (False, 'Emblem and vehTypeCompDescr mismatch')

        customization = vehicles.g_cache.customization(nationID)
        if custType == 'camouflages':
            if innationID not in customization['camouflages']:
                return (False, 'Unknown camouflage id')
            igrType = getCamouflageIGRType(nationID, innationID)
            if igrType != IGR_TYPE.NONE:
                return (False, 'Unexpected IGR camouflage')
        elif custType == 'inscriptions':
            if innationID not in customization['inscriptions']:
                return (False, 'Unknown inscription id')
            igrType = getPlayerInscriptionIGRType(nationID, innationID)
            if igrType != IGR_TYPE.NONE:
                return (False, 'Unexpected IGR inscription')
        elif custType == 'emblems':
            _, emblems, _ = vehicles.g_cache.playerEmblems()
            if innationID not in emblems:
                return (False, 'Unknown emblem id')
            igrType = getPlayerEmblemIGRType(innationID)
            if igrType != IGR_TYPE.NONE:
                return (False, 'Unexpected IGR emblem')
        return (True, '')


class NotificationItem(object):

    def __init__(self, item):
        self.item = item
        text = item['text']
        s = item['type'] + '\n'
        for k in sorted(text.keys()):
            s += k + '\n' + text[k] + '\n'

        s += item['data']
        self.asString = s

    def __cmp__(self, other):
        if other is None:
            return 1
        left = self.asString
        right = other.asString
        if left == right:
            return 0
        elif left < right:
            return -1
        else:
            return 1

    def __hash__(self):
        return hash(self.asString)
