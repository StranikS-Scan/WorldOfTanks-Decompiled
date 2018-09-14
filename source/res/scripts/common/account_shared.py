# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/account_shared.py
import time
import collections
import re
import nations
from items import vehicles, ITEM_TYPES
from constants import IGR_TYPE, FAIRPLAY_VIOLATIONS_NAMES, FAIRPLAY_VIOLATIONS_MASKS
from debug_utils import *

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
        assert False
    vehInfo = igrCustomizationLayout.get(vehInvID, None)
    if vehInfo is None:
        return default
    else:
        igrTypeInfo = vehInfo.get(accountIGRType, None)
        if igrTypeInfo is None:
            return default
        customInfo = igrTypeInfo.get(custType, None)
        return default if customInfo is None else customInfo.get(position, default)


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
                if propName == 'playerInscriptions':
                    data = getCustomizedComponentInIGR(igrCustomizationLayout, vehInvID, 'inscriptions', accountIGRType, pos, None)
                    if data[0] is not None:
                        vehDescr.setPlayerInscription(pos, *data)
                if propName == 'camouflages':
                    data = getCustomizedComponentInIGR(igrCustomizationLayout, vehInvID, 'camouflages', accountIGRType, pos, None)
                    if data[0] is not None:
                        vehDescr.setCamouflage(pos, *data)

        return vehDescr.makeCompactDescr()


def getCustomizedVehCompDescr(igrLayout, vehInvID, accountIGRType, vehCompDescr):
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
            raise Exception('Wrong camouflage idx')
        return descr['igrType']


def getPlayerInscriptionIGRType(nationID, inscriptionID):
    if inscriptionID is None:
        return IGR_TYPE.NONE
    else:
        customizationCache = vehicles.g_cache.customization(nationID)
        descr = customizationCache['inscriptions'].get(inscriptionID)
        if descr is None:
            raise Exception('Wrong inscription id')
        return descr[1]


def getPlayerEmblemIGRType(emblemID):
    if emblemID is None:
        return IGR_TYPE.NONE
    else:
        descr = vehicles.g_cache.playerEmblems()[1].get(emblemID)
        if descr is None:
            raise Exception('Wrong emblem idx')
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
        cont = []
        cont.append(item['type'])
        text = item['text']
        for k in sorted(text.keys()):
            cont.append(k)
            cont.append(text[k])

        cont.append(item['data'])
        for s in sorted(item['requiredTokens']):
            cont.append(s)

        self.asString = ''.join(cont)

    def __cmp__(self, other):
        if other is None:
            return 1
        left = self.asString
        right = other.asString
        if left == right:
            return 0
        else:
            return -1 if left < right else 1

    def __hash__(self):
        return hash(self.asString)


_VERSION_REGEXP = re.compile('^([a-z]{2,4}_)?([0-9]+\\.[0-9]+\\.[0-9]+)(_[0-9]+)?$')

def parseVersion(version):
    result = _VERSION_REGEXP.search(version)
    if result is None:
        return
    else:
        realmCode, mainVersion, patchVersion = result.groups()
        if mainVersion:
            realmCode = realmCode.replace('_', '') if realmCode else ''
            patchVersion = int(patchVersion.replace('_', '')) if patchVersion else 0
            return (realmCode, mainVersion, patchVersion)
        return


def isValidClientVersion(clientVersion, serverVersion):
    if clientVersion != serverVersion:
        if clientVersion is None or serverVersion is None:
            return False
        clientParsedVersion = parseVersion(clientVersion)
        serverParsedVersion = parseVersion(serverVersion)
        if clientParsedVersion is None or serverParsedVersion is None:
            return False
        clientRealmCode, clientMainVersion, clientPatchVersion = clientParsedVersion
        serverRealmCode, serverMainVersion, serverPatchVersion = serverParsedVersion
        if clientRealmCode != serverRealmCode:
            return False
        if clientMainVersion != serverMainVersion:
            return False
        if clientPatchVersion < serverPatchVersion:
            return False
    return True


def readClientServerVersion():
    import ResMgr
    fileName = 'scripts/entity_defs/Account.def'
    section = ResMgr.openSection(fileName)
    if section is None:
        raise Exception('Cannot open ' + fileName)
    for attrName, section in section['Properties'].items():
        if not attrName.startswith('requiredVersion_'):
            continue
        version = section.readString('Default')
        if not version:
            raise Exception('Subsection Account.def/Properties/%s/Default is missing or empty' % attrName)
        section = None
        ResMgr.purge(fileName)
        return (attrName, version)

    raise Exception('Field Account.def/Properties/requiredVersion_* is not found')
    return
