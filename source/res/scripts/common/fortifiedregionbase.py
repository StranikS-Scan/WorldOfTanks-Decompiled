# Embedded file name: scripts/common/FortifiedRegionBase.py
import time
import struct
from constants import FORT_BUILDING_TYPE, FORT_BUILDING_TYPE_NAMES, FORT_ORDER_TYPE, FORT_ORDER_TYPE_NAMES, SYS_MESSAGE_FORT_EVENT
from debug_utils import *
import dossiers2
import fortified_regions
from ops_pack import OpsPacker, OpsUnpacker, packPascalString, unpackPascalString, initOpsFormatDef
from UnitBase import UnitBase
NOT_ACTIVATED = -1
TOTAL_CONTRIBUTION = 0
FORT_AUTO_UNSUBSCRIBE_TIMEOUT = 60
SECONDS_PER_WEEK = 604800
MAX_BUILDING_POSITIONS = 2
NO_FORT_PACK = ''
EMPTY_FORT_PACK = ' '

class FORT_EVENT_TYPE:
    ACTIVE_ORDERS_BASE = 0
    DEFENCE_HOUR_CHANGE = 101
    DEFENCE_HOUR_COOLDOWN = 102
    OFF_DAY_CHANGE = 103
    OFF_DAY_COOLDOWN = 104
    VACATION_START = 105
    VACATION_COOLDOWN = 106
    PRODUCT_ORDERS_BASE = 200
    _COOLDOWNS = (DEFENCE_HOUR_COOLDOWN, OFF_DAY_COOLDOWN, VACATION_COOLDOWN)


class FORT_ERROR:
    OK = 0
    BAD_METHOD = 1
    NOT_CREATED = 2
    ALREADY_CREATED = 3
    NO_CLAN = 4
    DUPLICATE_BUILDING_TYPE = 5
    WRONG_POS = 6
    NO_BUILDING = 7
    NOT_ATTACHED_TO_BUILDING = 8
    STORAGE_OVERFLOW = 9
    EVENT_COOLDOWN = 10
    DEFENCE_NOT_POSSIBLE = 11
    DIR_NOT_OPEN = 12
    DIR_ALREADY_OPEN = 13
    NOT_ENOUGH_CLAN_MEMBERS = 14
    DIR_OCCUPIED = 15
    BAD_DIR = 16
    BAD_SORTIE_ID = 17
    TOO_MANY_PLAYERS_ATTACHED = 18
    ALREADY_ATTACHED = 19
    NO_DEST_BUILDING = 20
    NOT_ENOUGH_RESOURCE = 21
    CANT_UPGRADE = 22
    FORT_LEVEL_TOO_LOW = 23
    TRANSPORT_COOLDOWN = 24
    TRANSPORT_LIMIT_EXCEEDED = 25
    BAD_VACATION_START = 26
    BAD_VACATION_DURATION = 27
    NOT_A_CLAN_MEMBER = 28
    INSUFFICIENT_CLAN_ROLE = 29
    ORDER_ALREADY_IN_PRODUCTION = 30
    TOO_MANY_ORDERS = 31
    BUILDING_NOT_READY = 32
    WRONG_BUILDING = 33
    START_SCENARIO_NOT_DONE = 34
    CANT_TRANSPORT = 35
    NO_ORDER = 36
    NO_ORDER_DEF = 37
    NO_ORDER_LEVEL = 38
    BUILDINGS_STILL_PRESENT = 39
    DIRECTIONS_STILL_OPEN = 40
    TOO_MANY_SORTIES = 41
    METHOD_COOLDOWN = 42
    BAD_RESOURCE_COUNT = 43
    ORDER_ALREADY_ACTIVATED = 44
    ORDER_NOT_SUPPORTED = 45
    POSITION_OCCUPIED = 46
    BAD_SORTIE_DIVISION = 47
    NOT_SUPPORTED = 48
    PERIPHERY_NOT_CONNECTED = 49
    BAD_ORDERS_COUNT = 64


OK = FORT_ERROR.OK
FORT_ERROR_NAMES = dict([ (v, k) for k, v in FORT_ERROR.__dict__.iteritems() if not k.startswith('_') ])
MIL_BASE = FORT_BUILDING_TYPE.MILITARY_BASE

class FORT_OP:
    CREATE_NEW = 1
    ADD_BUILDING = 2
    DEL_BUILDING = 3
    CONTRIBUTE = 4
    ACTIVATE_ORDER = 5
    CHANGE_DEF_HOUR = 6
    EXPIRE_EVENT = 7
    SET_DEV_MODE = 8
    SET_TIME_SHIFT = 9
    OPEN_DIR = 10
    CLOSE_DIR = 11
    ADD_SORTIE = 12
    REMOVE_SORTIE = 13
    SORTIE_UNIT = 14
    ATTACH = 15
    DETACH = 16
    TRANSPORT = 17
    UPGRADE = 18
    UPDATE_ORDERS = 19
    REFRESH_CONTRIBS = 20
    DEL_ORDERS = 21
    CHANGE_PERIPHERY = 22
    CHANGE_OFF_DAY = 23
    CHANGE_VACATION = 24
    ADD_ORDERS = 25
    SET_STATE = 26
    DELETE = 27
    REQUEST = 28
    SYNC_DOSSIER = 29
    SET_RESOURCE = 100
    SET_DEF_HOUR = 101
    SET_OFF_DAY = 102
    SET_VACATION = 103


class FORT_URGENT_OP:
    ACTIVATE_ORDER = 1
    DEACTIVATE_ORDER = 2
    CREATE_SORTIE = 3
    SET_FORT_STATE = 4
    ORDER_PRODUCED = 5
    BUILDING_SYS_MESSAGE = 6


class FORT_NOTIFICATION:
    DING = 1


class FORT_STATE:
    FIRST_DIR_OPEN = 1
    FIRST_BUILD_START = 2
    FIRST_BUILD_DONE = 4
    FORT_CREATED = 8


class FORT_CONTRIBUTION_TYPE:
    CLIENT = 0
    DEFENCE = 1
    SORTIE_BASE = 100


class FORT_CLIENT_METHOD:
    CREATE = 1
    DELETE = 2
    SUBSCRIBE = 3
    UNSUBSCRIBE = 4
    OPEN_DIR = 5
    CLOSE_DIR = 6
    ADD_BUILDING = 7
    DEL_BUILDING = 8
    ATTACH = 9
    CONTRIBUTE = 10
    UPGRADE = 11
    TRANSPORT = 12
    ADD_ORDER = 13
    ACTIVATE_ORDER = 14
    CHANGE_DEF_HOUR = 15
    CHANGE_PERIPHERY = 16
    CHANGE_OFF_DAY = 17
    CHANGE_VACATION = 18
    SET_DEV_MODE = 19
    ADD_TIME_SHIFT = 20
    CREATE_SORTIE = 21
    GET_SORTIE_DATA = 22
    KEEPALIVE = 23


def makeDirPosByte(dir, pos):
    return dir << 4 | pos


def parseDirPosByte(dirPosByte):
    return (dirPosByte >> 4 & 15, dirPosByte & 15)


class BuildingDescr:
    FORMAT_HEADER = '<BBBBiiii'
    SIZE_HEADER = struct.calcsize(FORMAT_HEADER)

    def __init__(self, buildingCompactDescr = None, typeID = None, level = 0):
        if buildingCompactDescr is not None:
            self.__unpack(buildingCompactDescr)
            return
        else:
            self.__clear()
            if typeID is not None:
                self.typeRef = typeRef = fortified_regions.g_cache.buildings.get(typeID)
                normLevel = max(level, 1)
                self.levelRef = typeRef.levels.get(normLevel)
                self.typeID = typeID
                self.level = level
                if level:
                    self.hp = self.levelRef.hp
            return

    def __clear(self):
        self.typeRef = None
        self.levelRef = None
        self.typeID = 0
        self.level = 0
        self.hp = 0
        self.storage = 0
        self.direction = 0
        self.position = 0
        self.timeTransportCooldown = 0
        self.orderInProduction = {}
        self.attachedPlayers = set()
        return

    def __unpack(self, buildingCompactDescr):
        typeID, level, dirPosByte, productionCount, productionTimeFinish, resourceCount, self.timeTransportCooldown, attachedPlayersCount = struct.unpack_from(self.FORMAT_HEADER, buildingCompactDescr)
        self.typeRef = typeRef = fortified_regions.g_cache.buildings.get(typeID)
        normLevel = max(level, 1)
        self.levelRef = levelRef = typeRef.levels.get(normLevel)
        self.typeID = typeID
        self.level = level
        self.hp = min(resourceCount, levelRef.hp)
        self.storage = min(levelRef.storage, max(0, resourceCount - levelRef.hp))
        self.direction, self.position = parseDirPosByte(dirPosByte)
        if productionCount:
            self.orderInProduction = dict(count=productionCount, timeFinish=productionTimeFinish)
        else:
            self.orderInProduction = {}
        self.attachedPlayers = attachedPlayers = set()
        offset = self.SIZE_HEADER
        format = '<%dq' % attachedPlayersCount
        size = struct.calcsize(format)
        tupleUnpackedIDs = struct.unpack_from(format, buildingCompactDescr[offset:offset + size])
        attachedPlayers.update(tupleUnpackedIDs)

    def makeCompactDescr(self):
        resourceCount = self.hp + self.storage
        dirPosByte = makeDirPosByte(self.direction, self.position)
        orderInProduction = self.orderInProduction
        count = len(self.attachedPlayers)
        format = '%dq' % count
        compactDescr = struct.pack((self.FORMAT_HEADER + format), self.typeID, self.level, dirPosByte, orderInProduction.get('count', 0), orderInProduction.get('timeFinish', 0), resourceCount, self.timeTransportCooldown, count, *list(self.attachedPlayers))
        return compactDescr

    def incResource(self, resCount):
        levelRef = self.levelRef
        hpInc = min(resCount, max(levelRef.hp - self.hp, 0))
        self.hp += hpInc
        resCount -= hpInc
        if self.hp >= levelRef.hp and self.level == 0:
            self.level = 1
        storageInc = min(resCount, max(levelRef.storage - self.storage, 0))
        self.storage += storageInc
        resCount -= storageInc
        return resCount

    def setResource(self, resCount):
        LOG_DEBUG_DEV('%s setResource[%s:%s] %s' % (FORT_BUILDING_TYPE_NAMES.get(self.typeID, ''),
         self.hp,
         self.storage,
         resCount))
        levelRef = self.levelRef
        hp = min(max(0, resCount), levelRef.hp)
        self.hp = hp
        resCount -= hp
        if self.hp >= levelRef.hp and self.level == 0:
            self.level = 1
        storage = min(max(0, resCount), levelRef.storage)
        self.storage = storage
        resCount -= storage
        return resCount

    def isReady(self):
        if self.level == 0:
            return False
        if self.hp < self.levelRef.hp:
            return False
        return True

    def __repr__(self):
        repr = '[%s] t=%s, l=%s, hp=%s/%s, stor=%s/%s, pos=%s:%s, tCD=%s, inProd=%s(%s), attach=%s' % (FORT_BUILDING_TYPE_NAMES.get(self.typeID, ''),
         self.typeID,
         self.level,
         self.hp,
         self.levelRef.hp,
         self.storage,
         self.levelRef.storage,
         self.direction,
         self.position,
         self.timeTransportCooldown,
         self.orderInProduction.get('count', 0),
         self.orderInProduction.get('timeFinish', 0),
         self.attachedPlayers)
        return repr


class FortifiedRegionBase(OpsUnpacker):
    _opsFormatDefs = initOpsFormatDef({FORT_OP.CREATE_NEW: ('qi',
                          '_createNew',
                          'L',
                          [('i', 'q')]),
     FORT_OP.DELETE: ('q', '_delete'),
     FORT_OP.ADD_BUILDING: ('BBB', '_addBuilding'),
     FORT_OP.DEL_BUILDING: ('B', '_delBuilding'),
     FORT_OP.CONTRIBUTE: ('qBii', '_contribute'),
     FORT_OP.ACTIVATE_ORDER: ('Biiiiq', '_activateOrder'),
     FORT_OP.CHANGE_DEF_HOUR: ('Biiq', '_changeDefHour'),
     FORT_OP.CHANGE_PERIPHERY: ('H', '_changePeriphery'),
     FORT_OP.CHANGE_OFF_DAY: ('biiq', '_changeOffDay'),
     FORT_OP.CHANGE_VACATION: ('iiiq', '_changeVacation'),
     FORT_OP.EXPIRE_EVENT: ('Bi', '_expireEvent'),
     FORT_OP.SET_DEV_MODE: ('B', '_setDevMode'),
     FORT_OP.SET_TIME_SHIFT: ('i', '_setTimeShift'),
     FORT_OP.OPEN_DIR: ('B', '_openDir'),
     FORT_OP.CLOSE_DIR: ('B', '_closeDir'),
     FORT_OP.ADD_SORTIE: ('qqBHBBii',
                          '_setSortie',
                          'S',
                          ['']),
     FORT_OP.REMOVE_SORTIE: ('qH', '_removeSortie'),
     FORT_OP.SORTIE_UNIT: ('', '_unpackSortieUnit'),
     FORT_OP.ATTACH: ('Bq', '_attach'),
     FORT_OP.DETACH: ('Bq', '_detach'),
     FORT_OP.TRANSPORT: ('BBii', '_transport'),
     FORT_OP.UPGRADE: ('BBi', '_upgrade'),
     FORT_OP.UPDATE_ORDERS: ('BBBii', '_updateOrders'),
     FORT_OP.REFRESH_CONTRIBS: ('i', '_checkContributionExpiry'),
     FORT_OP.DEL_ORDERS: ('B', '_delOrders'),
     FORT_OP.ADD_ORDERS: ('Biiq', '_addOrders'),
     FORT_OP.SET_STATE: ('H', '_setState'),
     FORT_OP.REQUEST: ('iq', '_processRequest'),
     FORT_OP.SYNC_DOSSIER: ('',
                            '_syncFortDossier',
                            'S',
                            ['']),
     FORT_OP.SET_RESOURCE: ('Bi', '_setBuildingResource'),
     FORT_OP.SET_DEF_HOUR: ('i', '_setDefHour'),
     FORT_OP.SET_OFF_DAY: ('i', '_setOffDay'),
     FORT_OP.SET_VACATION: ('ii', '_setVacation')})
    FORMAT_HEADER = '<qiiiiHBbbBBBBBBBHH'
    SIZE_HEADER = struct.calcsize(FORMAT_HEADER)
    FORMAT_EVENT = '<Biiq'
    SIZE_EVENT = struct.calcsize(FORMAT_EVENT)
    FORMAT_BUILDING_HEADER = '<BH'
    SIZE_BUILDING_HEADER = struct.calcsize(FORMAT_BUILDING_HEADER)
    FORMAT_ORDER = '<BBh'
    SIZE_ORDER = struct.calcsize(FORMAT_ORDER)
    FORMAT_CONTRIBUTION_HEADER = '<qb'
    SIZE_CONTRIBUTION_HEADER = struct.calcsize(FORMAT_CONTRIBUTION_HEADER)
    FORMAT_CONTRIBUTION_ITEM = '<ii'
    SIZE_CONTRIBUTION_ITEM = struct.calcsize(FORMAT_CONTRIBUTION_ITEM)
    FORMAT_ADD_SORTIE_HEADER = '<qqBHBBii'
    SIZE_ADD_SORTIE_HEADER = struct.calcsize(FORMAT_ADD_SORTIE_HEADER)
    FORMAT_SORTIE_UNIT_HEADER = '<qH'
    SIZE_SORTIE_UNIT_HEADER = struct.calcsize(FORMAT_SORTIE_UNIT_HEADER)

    def __init__(self):
        self.statistics = None
        self._empty()
        return

    def _persist(self):
        pass

    def isEmpty(self):
        return self.dbID == 0

    def _empty(self):
        self.dbID = 0
        self._packed = EMPTY_FORT_PACK
        self._dirty = False

    def _getTime(self):
        return int(time.time()) + self._debugTimeShift

    def __repr__(self):
        if not self.dbID:
            return 'Fort: empty'
        s = 'Fort:\n ID=%s, p=%s, l=%s, s=%x, dM=%x, dH=%s, oD=%s, v=%s/%s, _D=%s, t+=%s\n ev=%s\n buildings(%s)' % (self.dbID,
         self.peripheryID,
         self.level,
         self.state,
         self.dirMask,
         self.defenceHour,
         self.offDay,
         self.vacationStart,
         self.vacationFinish,
         self._devMode,
         self._debugTimeShift,
         self.events,
         len(self.buildings))
        for buildID, buildCompDescr in self.buildings.iteritems():
            s += '\n  ' + repr(BuildingDescr(buildCompDescr))

        s += '\n orders(%s)' % len(self.orders)
        for orderID, rec in self.orders.iteritems():
            count, level = rec
            s += '\n  [%s] %sx%s ' % (FORT_ORDER_TYPE_NAMES.get(orderID, ''), count, level)

        s += '\n contribs(%s)' % len(self.playerContributions)
        for databaseID, dct in self.playerContributions.iteritems():
            s += '\n  [%s] %s' % (databaseID, dct)

        s += '\n sorties(%s)' % len(self.sorties)
        for sortieID, tpl in self.sorties.iteritems():
            s += '\n  [%s] %s' % (sortieID, tpl)

        return s

    def pack(self, isForced = False):
        if not self._dirty and not isForced:
            return self._packed
        self._dirty = False
        if self.dbID:
            statistics = self.statistics.makeCompDescr()
            packed = struct.pack(self.FORMAT_HEADER, self.dbID, self.peripheryID, self.vacationStart, self.vacationFinish, self._debugTimeShift, self.state, self.level, self.defenceHour, self.offDay, self._devMode, self.dirMask, len(self.events), len(self.buildings), len(self.orders), len(self.battles), len(self.sorties), len(self.playerContributions), len(statistics))
            for eventType, (unixtime, eventValue, initiatorDBID) in self.events.iteritems():
                packed += struct.pack(self.FORMAT_EVENT, eventType, unixtime, eventValue, initiatorDBID)

            for buildTypeID, buildingCompactDescr in self.buildings.iteritems():
                packed += struct.pack(self.FORMAT_BUILDING_HEADER, buildTypeID, len(buildingCompactDescr))
                packed += buildingCompactDescr

            for orderTypeID, (count, level) in self.orders.iteritems():
                packed += struct.pack(self.FORMAT_ORDER, orderTypeID, level, count)

            fmt = self.FORMAT_ADD_SORTIE_HEADER
            for (unitMgrID, peripheryID), rec in self.sorties.iteritems():
                cmdrDBID, rosterTypeID, count, maxCount, timestamp, igrType, cmdrName = rec
                packed += struct.pack(fmt, unitMgrID, cmdrDBID, rosterTypeID, peripheryID, count, maxCount, timestamp, igrType)
                packed += packPascalString(cmdrName)

            fmtHdr = self.FORMAT_CONTRIBUTION_HEADER
            fmtItem = self.FORMAT_CONTRIBUTION_ITEM
            for accountDBID, accDict in self.playerContributions.iteritems():
                packed += struct.pack(fmtHdr, accountDBID, len(accDict))
                for datestamp, resCount in accDict.iteritems():
                    packed += struct.pack(fmtItem, datestamp, resCount)

            packed += statistics
            self._packed = packed
        else:
            self._empty()
        self._persist()
        return self._packed

    def unpack(self, packedData):
        self._packed = packedData
        if len(packedData) <= 1:
            self._empty()
            return
        self._dirPosToBuildType = {}
        self._playerAttachments = {}
        packed = packedData
        self.dbID, self.peripheryID, self.vacationStart, self.vacationFinish, self._debugTimeShift, self.state, self.level, self.defenceHour, self.offDay, self._devMode, self.dirMask, lenEvents, lenBuildings, lenOrders, lenBattles, lenSorties, lenPlayerContributions, lenStatistics = struct.unpack_from(self.FORMAT_HEADER, packed)
        offset = self.SIZE_HEADER
        sz = self.SIZE_EVENT
        fmt = self.FORMAT_EVENT
        self.events = {}
        for i in xrange(lenEvents):
            eventType, unixtime, eventValue, initiatorDBID = struct.unpack_from(fmt, packed, offset)
            self.events[eventType] = (unixtime, eventValue, initiatorDBID)
            offset += sz

        sz = self.SIZE_BUILDING_HEADER
        fmt = self.FORMAT_BUILDING_HEADER
        self.buildings = {}
        for i in xrange(lenBuildings):
            buildTypeID, lenDescr = struct.unpack_from(fmt, packed, offset)
            offset += sz
            buildingCompactDescr = packed[offset:offset + lenDescr]
            self.buildings[buildTypeID] = buildingCompactDescr
            building = BuildingDescr(buildingCompactDescr)
            dirPos = makeDirPosByte(building.direction, building.position)
            self._dirPosToBuildType[dirPos] = buildTypeID
            for accountDBID in building.attachedPlayers:
                self._playerAttachments[accountDBID] = buildTypeID

            offset += lenDescr

        sz = self.SIZE_ORDER
        fmt = self.FORMAT_ORDER
        self.orders = {}
        for i in xrange(lenOrders):
            orderTypeID, level, count = struct.unpack_from(fmt, packed, offset)
            self.orders[orderTypeID] = (count, level)
            offset += sz

        sz = self.SIZE_ADD_SORTIE_HEADER
        fmt = self.FORMAT_ADD_SORTIE_HEADER
        self.sorties = {}
        self._sortieUnits = {}
        for i in xrange(lenSorties):
            unitMgrID, cmdrDBID, rosterTypeID, peripheryID, count, maxCount, timestamp, igrType = struct.unpack_from(fmt, packed, offset)
            cmdrName, lenCmdrName = unpackPascalString(packed, offset + sz)
            sortieKey = (unitMgrID, peripheryID)
            self.sorties[sortieKey] = (cmdrDBID,
             rosterTypeID,
             count,
             maxCount,
             timestamp,
             igrType,
             cmdrName)
            offset += sz + lenCmdrName

        szHdr = self.SIZE_CONTRIBUTION_HEADER
        szItem = self.SIZE_CONTRIBUTION_ITEM
        self.playerContributions = contributions = {}
        fmtHdr = self.FORMAT_CONTRIBUTION_HEADER
        fmtItem = self.FORMAT_CONTRIBUTION_ITEM
        for i in xrange(lenPlayerContributions):
            accountDBID, lenAccDict = struct.unpack_from(fmtHdr, packed, offset)
            dct = {}
            offset += szHdr
            for j in xrange(lenAccDict):
                datestamp, resCount = struct.unpack_from(fmtItem, packed, offset)
                dct[datestamp] = resCount
                offset += szItem

            contributions[accountDBID] = dct

        compDescr = packed[offset:offset + lenStatistics]
        self.statistics = dossiers2.getFortifiedRegionsDossierDescr(compDescr)
        offset += lenStatistics
        self.battles = {}
        raise offset == len(packed) or AssertionError

    def serialize(self):
        if not self.dbID:
            pdata = {}
            return pdata
        pdata = dict(dbID=self.dbID, attrs=(self.level,
         self.state,
         self.dirMask,
         self.peripheryID,
         self.defenceHour,
         self.offDay,
         self.vacationStart,
         self.vacationFinish,
         self._devMode,
         self._debugTimeShift), buildings=self.buildings, orders=self.orders, events=self.events, playerContributions=self.playerContributions, statistics=self.statistics.makeCompDescr())
        return pdata

    def deserialize(self, pdata):
        if not isinstance(pdata, dict) or not pdata:
            self._empty()
            return
        self.dbID = pdata['dbID']
        self._dirty = True
        if self.dbID:
            self.statistics = dossiers2.getFortifiedRegionsDossierDescr(pdata['statistics'])
            self.level, self.state, self.dirMask, self.peripheryID, self.defenceHour, self.offDay, self.vacationStart, self.vacationFinish, self._devMode, self._debugTimeShift = pdata['attrs']
            self.buildings = pdata['buildings']
            self.orders = pdata['orders']
            self.events = pdata['events']
            self.playerContributions = pdata['playerContributions']
            self.sorties = {}
            self._sortieUnits = {}
            self.battles = {}
            self._dirPosToBuildType = {}
            self._playerAttachments = {}
            for buildTypeID, buildingCompactDescr in self.buildings.iteritems():
                building = BuildingDescr(buildingCompactDescr)
                dirPos = makeDirPosByte(building.direction, building.position)
                self._dirPosToBuildType[dirPos] = buildTypeID
                for accountDBID in building.attachedPlayers:
                    self._playerAttachments[accountDBID] = buildTypeID

            self.state |= FORT_STATE.FORT_CREATED
        self.pack()

    def getBuilding(self, buildingTypeID):
        buildCompDescr = self.buildings.get(buildingTypeID)
        if buildCompDescr:
            return BuildingDescr(buildCompDescr)
        else:
            return None

    def setBuilding(self, buildingTypeID, buildingDescr):
        self.buildings[buildingTypeID] = buildingDescr.makeCompactDescr()

    def checkDefenceConditions(self):
        return True

    def _checkContributionExpiry(self, timeThreshold):
        isDirty = False
        for accDBID, contributionRecord in self.playerContributions.iteritems():
            for stamp in contributionRecord.keys():
                if stamp != TOTAL_CONTRIBUTION and stamp < timeThreshold:
                    del contributionRecord[stamp]
                    isDirty = True

        if isDirty:
            LOG_DEBUG_DEV('_checkContributionExpiry', timeThreshold)
            self.storeOp(FORT_OP.REFRESH_CONTRIBS, timeThreshold)

    def getPlayerContributions(self, accDBID):
        lastWeekThreshold = self._getTime() - SECONDS_PER_WEEK
        contributionRecord = self.playerContributions.get(accDBID, {})
        total = contributionRecord.get(TOTAL_CONTRIBUTION, 0)
        lastWeek = 0
        for stamp, value in contributionRecord.iteritems():
            if stamp != TOTAL_CONTRIBUTION and stamp >= lastWeekThreshold:
                lastWeek += value

        return (total, lastWeek)

    def _DEBUG_createFake(self):
        if self.dbID:
            return FORT_ERROR.ALREADY_CREATED
        self.dbID = 123
        self.state = 0
        self._devMode = IS_DEVELOPMENT
        self._debugTimeShift = 0
        now = self._getTime()
        self.peripheryID = 2
        self.defenceHour = 23
        self.offDay = 6
        self.vacationStart = now + 432000
        self.vacationFinish = now + 1296000
        self.events = {FORT_EVENT_TYPE.DEFENCE_HOUR_CHANGE: (now + 259200, 22, 0),
         FORT_EVENT_TYPE.OFF_DAY_CHANGE: (now + 172800, 5, 0),
         FORT_EVENT_TYPE.DEFENCE_HOUR_COOLDOWN: (now + 1036800, 0, 0),
         FORT_EVENT_TYPE.OFF_DAY_COOLDOWN: (now + 1209600, 0, 0),
         FORT_EVENT_TYPE.VACATION_COOLDOWN: (now + 5184000, 0, 0)}
        clanMemberDBIDs = set([1234,
         2,
         3,
         4,
         5])
        self.level = 2
        self.dirMask = 3
        self.buildings = {}
        self._dirPosToBuildType = {}
        building = BuildingDescr(typeID=FORT_BUILDING_TYPE.MILITARY_BASE, level=2)
        building.attachedPlayers = set([1234, 2, 3])
        self.buildings[building.typeID] = building.makeCompactDescr()
        dirPos = makeDirPosByte(building.direction, building.position)
        self._dirPosToBuildType[dirPos] = building.typeID
        self._playerAttachments = dict.fromkeys(building.attachedPlayers, building.typeID)
        building = BuildingDescr(typeID=FORT_BUILDING_TYPE.FINANCIAL_DEPT, level=1)
        building.direction = 1
        building.orderInProduction = {'count': 5,
         'timeFinish': now + 7200}
        building.hp = 5
        building.attachedPlayers = set([4])
        self.buildings[building.typeID] = building.makeCompactDescr()
        dirPos = makeDirPosByte(building.direction, building.position)
        self._dirPosToBuildType[dirPos] = building.typeID
        id = building.typeID
        self._playerAttachments.update({4: id})
        building = BuildingDescr(typeID=FORT_BUILDING_TYPE.TANKODROME, level=0)
        building.direction = 1
        building.position = 1
        building.hp = 5
        building.attachedPlayers = set()
        self.buildings[building.typeID] = building.makeCompactDescr()
        dirPos = makeDirPosByte(building.direction, building.position)
        self._dirPosToBuildType[dirPos] = building.typeID
        building = BuildingDescr(typeID=FORT_BUILDING_TYPE.TRAINING_DEPT, level=1)
        building.direction = 2
        building.position = 0
        building.storage = building.levelRef.storage
        building.attachedPlayers = set([5])
        self.buildings[building.typeID] = building.makeCompactDescr()
        dirPos = makeDirPosByte(building.direction, building.position)
        self._dirPosToBuildType[dirPos] = building.typeID
        id = building.typeID
        self._playerAttachments.update({5: id})
        self.playerContributions = {1234: {TOTAL_CONTRIBUTION: 250},
         2: {TOTAL_CONTRIBUTION: 150},
         3: {TOTAL_CONTRIBUTION: 120},
         4: {TOTAL_CONTRIBUTION: 30},
         5: {}}
        self.orders = {FORT_ORDER_TYPE.COMBAT_PAYMENTS: (10, 1),
         FORT_ORDER_TYPE.TACTICAL_TRAINING: (15, 1)}
        self.plannedAttacks = []
        self.plannedDefences = []
        self.battles = {}
        self.sorties = {}
        self._sortieUnits = {}
        self.statistics = dossiers2.getFortifiedRegionsDossierDescr()
        self._dirty = True

    def _addBuilding(self, buildingTypeID, dir, pos):
        LOG_DEBUG_DEV('_addBuilding', buildingTypeID, dir, pos)
        building = BuildingDescr(typeID=buildingTypeID, level=0)
        building.direction = dir
        building.position = pos
        self.buildings[buildingTypeID] = building.makeCompactDescr()
        dirPos = makeDirPosByte(dir, pos)
        self._dirPosToBuildType[dirPos] = buildingTypeID
        self.storeOp(FORT_OP.ADD_BUILDING, buildingTypeID, dir, pos)

    def _delBuilding(self, buildingTypeID):
        LOG_DEBUG_DEV('_delBuilding', buildingTypeID)
        building = self.getBuilding(buildingTypeID)
        dirPos = makeDirPosByte(building.direction, building.position)
        self._dirPosToBuildType.pop(dirPos)
        if building.attachedPlayers:
            milBase = self.getBuilding(MIL_BASE)
            milBase.attachedPlayers.update(building.attachedPlayers)
            for accDBID in building.attachedPlayers:
                self._playerAttachments[accDBID] = MIL_BASE

            self.setBuilding(MIL_BASE, milBase)
        self.buildings.pop(buildingTypeID)
        orderTypeID = buildingTypeID + FORT_EVENT_TYPE.PRODUCT_ORDERS_BASE
        self.events.pop(orderTypeID, None)
        self.storeOp(FORT_OP.DEL_BUILDING, buildingTypeID)
        return

    def _recalcOrders(self, orderTypeID, prevCount, prevLevel, newLevel):
        orderLevels = fortified_regions.g_cache.orders[orderTypeID].levels
        prevCost = orderLevels[prevLevel].productionCost
        newCost = orderLevels[newLevel].productionCost
        newCount = prevCount * prevCost / newCost
        resLeft = prevCount * prevCost % newCost
        return (newCount, resLeft)

    def _delOrders(self, orderTypeID):
        LOG_DEBUG_DEV('_delOrders', orderTypeID)
        self.orders.pop(orderTypeID, None)
        self.storeOp(FORT_OP.DEL_ORDERS, orderTypeID)
        return

    def _addOrders(self, buildingTypeID, count, timeFinish, initiatorDBID):
        LOG_DEBUG_DEV('_addOrders', buildingTypeID, count, timeFinish, initiatorDBID)
        self.storeOp(FORT_OP.ADD_ORDERS, buildingTypeID, count, timeFinish, initiatorDBID)
        building = self.getBuilding(buildingTypeID)
        orderTypeID = building.typeRef.orderType
        level = building.level
        orderLevel = fortified_regions.g_cache.orders[orderTypeID].levels[level]
        building.storage -= orderLevel.productionCost * count
        now = self._getTime()
        timeFinish = orderLevel.productionTime * count + now
        building.orderInProduction = dict(count=count, timeFinish=timeFinish)
        self.setBuilding(buildingTypeID, building)
        eventID = FORT_EVENT_TYPE.PRODUCT_ORDERS_BASE + buildingTypeID
        self.events[eventID] = (timeFinish, level, initiatorDBID)
        LOG_DEBUG_DEV('_addOrders times:', self._getTime(), timeFinish)

    def _contribute(self, accDBID, buildingTypeID, resCount, dateStamp):
        LOG_DEBUG_DEV('_contribute', accDBID, buildingTypeID, resCount, dateStamp)
        self.storeOp(FORT_OP.CONTRIBUTE, accDBID, buildingTypeID, resCount, dateStamp)
        building = self.getBuilding(buildingTypeID)
        leftResCount = building.incResource(resCount)
        self.setBuilding(buildingTypeID, building)
        contributionRecord = self.playerContributions.setdefault(accDBID, {})
        contributionRecord[TOTAL_CONTRIBUTION] = contributionRecord.get(TOTAL_CONTRIBUTION, 0) + resCount
        contributionRecord[dateStamp] = contributionRecord.get(dateStamp, 0) + resCount
        return leftResCount

    def _createNew(self, clanDBID, peripheryID, clanMemberDBIDs):
        LOG_DAN('Fort._createNew', clanDBID, peripheryID, clanMemberDBIDs)
        self.dbID = clanDBID
        self.state = FORT_STATE.FORT_CREATED
        self.peripheryID = peripheryID
        self.defenceHour = NOT_ACTIVATED
        self.offDay = NOT_ACTIVATED
        self.vacationStart = 0
        self.vacationFinish = 0
        self.events = {}
        self.level = 1
        self.dirMask = 0
        self._devMode = IS_DEVELOPMENT
        self._debugTimeShift = 0
        self.buildings = {}
        building = BuildingDescr(typeID=FORT_BUILDING_TYPE.MILITARY_BASE, level=1)
        building.storage = fortified_regions.g_cache.startResource
        building.attachedPlayers = set(clanMemberDBIDs)
        self.buildings[FORT_BUILDING_TYPE.MILITARY_BASE] = building.makeCompactDescr()
        self._dirPosToBuildType = {0: [FORT_BUILDING_TYPE.MILITARY_BASE]}
        self._playerAttachments = dict.fromkeys(clanMemberDBIDs, FORT_BUILDING_TYPE.MILITARY_BASE)
        self.playerContributions = {}
        self.orders = {}
        self.plannedAttacks = []
        self.plannedDefences = []
        self.battles = {}
        self.sorties = {}
        self._sortieUnits = {}
        self.statistics = dossiers2.getFortifiedRegionsDossierDescr()
        self.storeOp(FORT_OP.CREATE_NEW, clanDBID, peripheryID, clanMemberDBIDs)

    SIZE_CREATE_NEW_HEADER = struct.calcsize('<qii')
    SIZE_DBID = struct.calcsize('<q')

    def _delete(self, deleterDBID):
        LOG_DAN('Fort._delete', deleterDBID)
        self.storeOp(FORT_OP.DELETE, deleterDBID)
        self._empty()

    def _activateOrder(self, orderTypeID, timeExpiration, effectValue, count, level, initiatorDBID):
        LOG_DEBUG_DEV('_activateOrder', orderTypeID, timeExpiration, effectValue, count, level, initiatorDBID)
        if count:
            self.orders[orderTypeID] = (count, level)
        else:
            self.orders.pop(orderTypeID, None)
        eventID = FORT_EVENT_TYPE.ACTIVE_ORDERS_BASE + orderTypeID
        self.events[eventID] = (timeExpiration, effectValue, initiatorDBID)
        self.storeOp(FORT_OP.ACTIVATE_ORDER, orderTypeID, timeExpiration, effectValue, count, level, initiatorDBID)
        return

    def _changeDefHour(self, newValue, timeActivation, timeCooldown, initiatorDBID):
        LOG_DEBUG_DEV('_changeDefHour', newValue, timeActivation, timeCooldown, initiatorDBID)
        self.events[FORT_EVENT_TYPE.DEFENCE_HOUR_CHANGE] = (timeActivation, newValue, initiatorDBID)
        self.events[FORT_EVENT_TYPE.DEFENCE_HOUR_COOLDOWN] = (timeCooldown, 0, 0)
        self.storeOp(FORT_OP.CHANGE_DEF_HOUR, newValue, timeActivation, timeCooldown, initiatorDBID)

    def _changePeriphery(self, peripheryID):
        LOG_DEBUG_DEV('_changePeriphery', peripheryID)
        self.peripheryID = peripheryID
        self.storeOp(FORT_OP.CHANGE_PERIPHERY, peripheryID)

    def _changeOffDay(self, offDay, timeActivation, timeCooldown, initiatorDBID):
        LOG_DEBUG_DEV('_changeOffDay', offDay, timeActivation, timeCooldown, initiatorDBID)
        self.events[FORT_EVENT_TYPE.OFF_DAY_CHANGE] = (timeActivation, offDay, initiatorDBID)
        self.events[FORT_EVENT_TYPE.OFF_DAY_COOLDOWN] = (timeCooldown, 0, 0)
        self.storeOp(FORT_OP.CHANGE_OFF_DAY, offDay, timeActivation, timeCooldown, initiatorDBID)

    def _changeVacation(self, timeVacationStart, timeVacationEnd, timeCooldown, initiatorDBID):
        LOG_DEBUG_DEV('_changeVacation', timeVacationStart, timeVacationEnd, timeCooldown, initiatorDBID)
        self.vacationStart = timeVacationStart
        self.vacationFinish = timeVacationEnd
        self.events[FORT_EVENT_TYPE.VACATION_START] = (timeVacationStart, timeVacationEnd, initiatorDBID)
        self.events[FORT_EVENT_TYPE.VACATION_COOLDOWN] = (timeCooldown, 0, 0)
        self.storeOp(FORT_OP.CHANGE_VACATION, timeVacationStart, timeVacationEnd, timeCooldown, initiatorDBID)

    def _expireEvent(self, eventTypeID, value):
        LOG_DEBUG_DEV('_expireEvent', eventTypeID, value)
        self.events.pop(eventTypeID, None)
        buildingTypeID = eventTypeID - FORT_EVENT_TYPE.PRODUCT_ORDERS_BASE
        if buildingTypeID in FORT_BUILDING_TYPE_NAMES:
            building = self.getBuilding(buildingTypeID)
            building.orderInProduction.clear()
            self.setBuilding(buildingTypeID, building)
        elif eventTypeID == FORT_EVENT_TYPE.DEFENCE_HOUR_CHANGE:
            self.defenceHour = value
        elif eventTypeID == FORT_EVENT_TYPE.OFF_DAY_CHANGE:
            self.offDay = value
        elif eventTypeID == FORT_EVENT_TYPE.VACATION_START:
            pass
        self.storeOp(FORT_OP.EXPIRE_EVENT, eventTypeID, value)
        return

    def _setDevMode(self, isActive):
        LOG_DEBUG_DEV('_setDevMode', isActive)
        self._devMode = bool(isActive)
        self.storeOp(FORT_OP.SET_DEV_MODE, int(isActive))

    def _setTimeShift(self, timeShift):
        LOG_DEBUG_DEV('_setTimeShift', timeShift)
        self._debugTimeShift = timeShift
        self.storeOp(FORT_OP.SET_TIME_SHIFT, timeShift)

    def _openDir(self, dir):
        LOG_DEBUG_DEV('_openDir', dir)
        self.dirMask |= 1 << dir
        self.storeOp(FORT_OP.OPEN_DIR, dir)

    def _closeDir(self, dir):
        LOG_DEBUG_DEV('_closeDir', dir)
        self.dirMask &= ~(1 << dir)
        self.storeOp(FORT_OP.CLOSE_DIR, dir)

    def _attach(self, buildTypeID, accDBID):
        LOG_DEBUG_DEV('_attach', buildTypeID, accDBID)
        building = self.getBuilding(buildTypeID)
        building.attachedPlayers.add(accDBID)
        self._playerAttachments[accDBID] = buildTypeID
        self.setBuilding(buildTypeID, building)
        self.storeOp(FORT_OP.ATTACH, buildTypeID, accDBID)

    def _detach(self, buildTypeID, accDBID):
        LOG_DEBUG_DEV('_detach', buildTypeID, accDBID)
        building = self.getBuilding(buildTypeID)
        building.attachedPlayers.remove(accDBID)
        self._playerAttachments.pop(accDBID, None)
        self.setBuilding(buildTypeID, building)
        self.storeOp(FORT_OP.DETACH, buildTypeID, accDBID)
        return

    def _transport(self, fromBuildTypeID, toBuildTypeID, resCount, timeCooldown):
        LOG_DEBUG_DEV('_transport', fromBuildTypeID, toBuildTypeID, resCount, timeCooldown)
        building = self.getBuilding(fromBuildTypeID)
        building.storage -= resCount
        self.setBuilding(fromBuildTypeID, building)
        building = self.getBuilding(toBuildTypeID)
        building.incResource(resCount)
        building.timeTransportCooldown = timeCooldown
        self.setBuilding(toBuildTypeID, building)
        self.storeOp(FORT_OP.TRANSPORT, fromBuildTypeID, toBuildTypeID, resCount, timeCooldown)

    def _upgrade(self, buildTypeID, level, decStorage):
        LOG_DEBUG_DEV('_upgrade', buildTypeID, level, decStorage)
        building = self.getBuilding(buildTypeID)
        building.level = level
        building.levelRef = levelRef = building.typeRef.levels.get(level)
        building.hp = levelRef.hp
        building.storage -= decStorage
        self.setBuilding(buildTypeID, building)
        if buildTypeID == FORT_BUILDING_TYPE.MILITARY_BASE:
            self.level = level
        self.storeOp(FORT_OP.UPGRADE, buildTypeID, level, decStorage)

    def _updateOrders(self, orderTypeID, buildingTypeID, newLevel, newCount, resLeft):
        LOG_DEBUG_DEV('_updateOrders', orderTypeID, buildingTypeID, newLevel, newCount, resLeft)
        self.storeOp(FORT_OP.UPDATE_ORDERS, orderTypeID, buildingTypeID, newLevel, newCount, resLeft)
        if newCount:
            self.orders[orderTypeID] = (newCount, newLevel)
        else:
            self.orders.pop(orderTypeID, None)
        if resLeft:
            building = self.getBuilding(buildingTypeID)
            building.incResource(resLeft)
            self.setBuilding(buildingTypeID, building)
        return

    def _setSortie(self, unitMgrID, cmdrDBID, rosterTypeID, peripheryID, count, maxCount, timestamp, igrType, cmdrName):
        LOG_DEBUG_DEV('_setSortie', unitMgrID, cmdrDBID, rosterTypeID, peripheryID, count, maxCount, timestamp, igrType, cmdrName)
        sortieKey = (unitMgrID, peripheryID)
        sortieArgs = (cmdrDBID,
         rosterTypeID,
         count,
         maxCount,
         timestamp,
         igrType,
         cmdrName)
        self.sorties[sortieKey] = sortieArgs
        self.storeOp(FORT_OP.ADD_SORTIE, unitMgrID, cmdrDBID, rosterTypeID, peripheryID, count, maxCount, timestamp, igrType, cmdrName)

    def _removeSortie(self, unitMgrID, peripheryID):
        LOG_DEBUG_DEV('_removeSortie', unitMgrID, peripheryID)
        sortieKey = (unitMgrID, peripheryID)
        self.sorties.pop(sortieKey, None)
        self._sortieUnits.pop(sortieKey, None)
        self.storeOp(FORT_OP.REMOVE_SORTIE, unitMgrID, peripheryID)
        return

    def _unpackSortieUnit(self, unpacking):
        unitMgrID, peripheryID = struct.unpack_from(self.FORMAT_SORTIE_UNIT_HEADER, unpacking)
        unit = UnitBase()
        unpacking = unit.unpack(unpacking[self.SIZE_SORTIE_UNIT_HEADER:])
        sortieKey = (unitMgrID, peripheryID)
        self._sortieUnits[sortieKey] = unit.pack()
        LOG_DEBUG_DEV('_unpackSortieUnit', unitMgrID, peripheryID, unit)
        return unpacking

    def _setState(self, newState):
        LOG_DEBUG_DEV('_setState', newState)
        self.state = newState
        self.storeOp(FORT_OP.SET_STATE, newState)

    def _processRequest(self, reqID, callerDBID):
        LOG_DEBUG_DEV('_processRequest', reqID, callerDBID)

    def _syncFortDossier(self, compDossierDescr):
        self.statistics = dossiers2.getFortifiedRegionsDossierDescr(compDossierDescr)
        LOG_DEBUG_DEV('_syncFortDossier', self.statistics['total'], self.statistics['achievements'], self.statistics['fortSorties'], self.statistics['fortBattles'])

    def _setBuildingResource(self, buildingTypeID, resCount):
        LOG_DEBUG_DEV('_setBuildingResource', buildingTypeID, resCount)
        building = self.getBuilding(buildingTypeID)
        building.setResource(resCount)
        self.setBuilding(buildingTypeID, building)
        self.storeOp(FORT_OP.SET_RESOURCE, buildingTypeID, resCount)

    def _setDefHour(self, defHour):
        LOG_DEBUG_DEV('_setDefHour', defHour)
        self.defenceHour = defHour
        self.storeOp(FORT_OP.SET_DEF_HOUR, defHour)

    def _setOffDay(self, offDay):
        LOG_DEBUG_DEV('_setOffDay', offDay)
        self.offDay = offDay
        self.storeOp(FORT_OP.SET_OFF_DAY, offDay)

    def _setVacation(self, timeStart, timeEnd):
        LOG_DEBUG_DEV('_setVacation', timeStart, timeEnd)
        self.vacationStart = timeStart
        self.vacationFinish = timeEnd
        self.events[FORT_EVENT_TYPE.VACATION_START] = (timeStart, timeEnd, 0)
        self.storeOp(FORT_OP.SET_VACATION, timeStart, timeEnd)
