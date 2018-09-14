# Embedded file name: scripts/common/FortifiedRegionBase.py
import time
import struct
import random
import cPickle
import dossiers2
import fortified_regions
from constants import FORT_BUILDING_TYPE, FORT_BUILDING_TYPE_NAMES, FORT_ORDER_TYPE, FORT_ORDER_TYPE_NAMES, SYS_MESSAGE_FORT_EVENT, FORT_BUILDING_STATUS, IS_KOREA, IS_DEVELOPMENT
from constants import CLAN_MEMBER_FLAGS
from ops_pack import OpsUnpacker, packPascalString, unpackPascalString, initOpsFormatDef
from UnitBase import UnitBase
from debug_utils import LOG_DEBUG_DEV, LOG_DAN, LOG_CURRENT_EXCEPTION, LOG_VLK, LOG_WARNING, LOG_OGNICK_DEV, LOG_OGNICK
from UnitRoster import buildNamesDict
NOT_ACTIVATED = -1
TOTAL_CONTRIBUTION = 0
FORT_AUTO_UNSUBSCRIBE_TIMEOUT = 60
SECONDS_PER_HOUR = 60 * 60
SECONDS_PER_DAY = 24 * SECONDS_PER_HOUR
SECONDS_PER_WEEK = 7 * SECONDS_PER_DAY
INT_MAX = (1 << 31) - 1
INT_MIN = -(1 << 31)
OFF_DAY_SETTING_PERIOD = 10
MAX_BUILDING_POSITIONS = 2
MAX_DIRECTION_NUM = 6
NO_FORT_PACK = ''
EMPTY_FORT_PACK = ' '
FORT_BATTLE_BUILDING_HP_PERCENT = 20
DEF_SHUTDOWN_LEVEL = 4
MAX_PERIPHERY_ID = 999
ALL_DIRS = 100

class FORT_EVENT_TYPE():
    ACTIVE_ORDERS_BASE = 0
    DIR_OPEN_ATTACKS_BASE = 90
    DIR_OPEN_ATTACKS_FIRST = DIR_OPEN_ATTACKS_BASE + 1
    DIR_OPEN_ATTACKS_LAST = DIR_OPEN_ATTACKS_BASE + MAX_DIRECTION_NUM
    DEFENCE_HOUR_CHANGE = 101
    DEFENCE_HOUR_COOLDOWN = 102
    OFF_DAY_CHANGE = 103
    OFF_DAY_COOLDOWN = 104
    VACATION_START = 105
    VACATION_COOLDOWN = 106
    VACATION_FINISH = 107
    DEFENCE_HOUR_SHUTDOWN = 108
    PERIPHERY_COOLDOWN = 109
    OFF_DAY_SETTING = 110
    BUILDING_MAPS_BASE = 150
    PRODUCT_ORDERS_BASE = 200
    _COOLDOWNS = (DEFENCE_HOUR_COOLDOWN,
     OFF_DAY_COOLDOWN,
     VACATION_COOLDOWN,
     PERIPHERY_COOLDOWN)
    _DIR_OPEN_EVENTS = range(DIR_OPEN_ATTACKS_FIRST, DIR_OPEN_ATTACKS_LAST + 1)
    _BUILDING_MAPS_EVENTS = range(BUILDING_MAPS_BASE, BUILDING_MAPS_BASE + 20)
    _SHUTDOWN_EVENTS = set([DEFENCE_HOUR_CHANGE,
     DEFENCE_HOUR_COOLDOWN,
     OFF_DAY_CHANGE,
     OFF_DAY_COOLDOWN,
     VACATION_START,
     VACATION_COOLDOWN,
     VACATION_FINISH,
     PERIPHERY_COOLDOWN] + _DIR_OPEN_EVENTS + _BUILDING_MAPS_EVENTS)


class FORT_ERROR():
    WAIT_OK = -1
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
    NO_DATA_FOR_ACTIVATING_ORDER = 50
    TOO_FEW_OPEN_DIRS = 51
    DEF_HOUR_NOT_ACTIVE = 52
    SHUTDOWN_ALREADY_REQUESTED = 53
    SHUTDOWN_NOT_REQUESTED = 54
    NO_PRODUCTION_ORDER = 55
    ORDER_ALREADY_SUSPENDED = 56
    ORDER_NOT_SUSPENDED = 57
    GLOBAL_PRODUCTION_SUSPEND = 58
    BUILDING_DAMAGED = 59
    BASE_DAMAGED = 60
    BASE_NOT_DAMAGED = 61
    DIRECTION_CONTESTED = 62
    BASE_DESTROYED = 63
    BAD_ORDERS_COUNT = 64
    BAD_HOUR_VALUE = 65
    BAD_DAY_VALUE = 66
    BATTLE_DOES_NOT_EXIST = 67
    UNIT_NOT_READY = 68
    BAD_FORT_BATTLE_ID = 69
    WRONG_CLAN = 70
    ATTACK_DIR_BUSY = 71
    DEFENCE_DIR_BUSY = 72
    FAILED_TO_BOOK_DIR = 73
    DIR_LOCKED = 74
    NON_ALIGNED_TIMESTAMP = 75
    CLAN_ON_VACATION = 76
    CLAN_HAS_OFF_DAY = 77
    DIR_NOT_OPEN_FOR_ATTACKS = 78
    ALREADY_PLANNED_ATTACK = 79
    ATTACK_COOLDOWN = 80
    ATTACK_PREORDER_FAILED = 81
    SCR_DIR_LOCKED = 82
    DEST_DIR_LOCKED = 83
    NO_SUCH_ATTACK = 84
    ATTACK_NOT_PLANNED = 85
    DEFENCE_NOT_PLANNED = 86
    ATTACKS_NOT_LOADED = 87
    ALREADY_FAVORITE = 88
    BAD_CLAN_DBID = 89
    NOT_FAVORITE = 90
    BAD_DMG = 91
    CANT_CREATE_CLAN = 92
    CANT_LOOKUP_CLAN = 93
    WRONG_PERIPHERY = 94
    FORT_BATTLES_DISABLED = 95
    TOO_MANY_DEFENCES = 96
    CURFEW_HOUR = 97
    LAST_DIR_FOR_DEFENCE = 98
    JOIN_CTX_LOCKED = 99
    NOT_BATTLE_CREATOR = 100
    WRONG_SLOT_INDEX = 101
    BATTLE_ROUND_IN_PROGRESS = 102
    NOT_ATTACHED_TO_BATTLE = 103
    NOT_SCHEDULED = 104
    TOO_MANY_FAVORITES = 105
    ATTACK_TOO_LATE = 106
    BAD_FORT_BATTLE_DIVISION = 107
    FORBIDDEN_FORT_BATTLE_HOUR = 108
    EQUIPMENTS_NOT_AVAILABLE = 109
    LEGIONARE_FORT_RESOURCE = 110
    BAD_SORTIE_TIME = 111
    BAD_SORTIE_PERIPHERY_ID = 112


OK = FORT_ERROR.OK
FORT_ERROR_NAMES = dict([ (v, k) for k, v in FORT_ERROR.__dict__.iteritems() if not k.startswith('_') ])
MIL_BASE = FORT_BUILDING_TYPE.MILITARY_BASE

class FORT_OP():
    CREATE_NEW = 1
    ADD_BUILDING = 2
    DEL_BUILDING = 3
    CONTRIBUTE = 4
    ACTIVATE_ORDER = 5
    ACTIVATE_DEF_HOUR = 6
    CHANGE_DEF_HOUR = 7
    EXPIRE_EVENT = 8
    SET_DEV_MODE = 9
    SET_TIME_SHIFT = 10
    OPEN_DIR = 11
    CLOSE_DIR = 12
    ADD_SORTIE = 13
    REMOVE_SORTIE = 14
    SORTIE_UNIT = 15
    ATTACH = 16
    DETACH = 17
    TRANSPORT = 18
    UPGRADE = 19
    UPDATE_ORDERS = 20
    REFRESH_CONTRIBS = 21
    DEL_ORDERS = 22
    CHANGE_PERIPHERY = 23
    CHANGE_OFF_DAY = 24
    CHANGE_VACATION = 25
    ADD_ORDERS = 26
    SET_STATE = 27
    DELETE = 28
    REQUEST = 29
    SYNC_DOSSIER = 30
    SHUTDOWN_DEF_HOUR = 31
    CANCEL_EVENT = 32
    DMG_BUILDING = 33
    SUSPEND_PRODUCTION = 34
    RESUME_PRODUCTION = 35
    ENEMY_CLAN_CARD = 36
    DELETE_BATTLES_BY_TIME = 37
    DELETE_BATTLES_BY_CLAN = 38
    ADD_ATTACK = 39
    ADD_DEFENCE = 40
    SET_LOCKED_DIRS = 41
    SET_ATTACK_RESULT = 42
    ADD_FORT_BATTLE = 43
    REMOVE_FORT_BATTLE = 44
    SET_FORT_BATTLE_BUILDNUM = 45
    SET_FORT_BATTLE_DIRECTIONS = 46
    FORT_BATTLE_UNIT = 47
    REMOVE_FORT_BATTLE_UNIT = 48
    SET_FORT_BATTLE_ROUND = 49
    ADD_FAVORITE = 50
    REMOVE_FAVORITE = 51
    SET_BUILD_MAPS = 52
    SET_ENEMY_READY_FOR_BATTLE = 53
    EMERGENCY_ON_RESTORE = 54
    ADD_EVENT = 55
    CHANGE_ORDER_COUNT = 56
    REPLACE_CONSUMABLES = 57
    SET_FORT_BATTLE_RESULTS = 58
    DELETE_BATTLE_BY_ID = 59
    ADD_INFLUENCE_POINTS = 60
    SET_UNIT_MGR_IS_DEAD = 61
    DELETE_CONSUMABLES = 62
    SET_RESOURCE = 101
    SET_DEF_HOUR = 102
    SET_OFF_DAY = 103
    SET_VACATION = 104
    SET_PERIPHERY = 105
    SET_INFLUENCE_POINTS = 106


class FORT_URGENT_OP():
    ACTIVATE_ORDER = 1
    DEACTIVATE_ORDER = 2
    CREATE_SORTIE = 3
    SET_FORT_STATE = 4
    ORDER_PRODUCED = 5
    BUILDING_SYS_MESSAGE = 6
    GENERIC_SYS_MESSAGE = 7
    CREATE_FORT_BATTLE = 8
    JOIN_FORT_BATTLE = 9
    CHANGE_PERIPHERY_SYS_MESSAGE = 10
    ORDER_COMPENSATED = 11
    ACTIVATE_SPECIAL_MISSION = 12


class FORT_NOTIFICATION():
    DING = 1


class FORT_STATE():
    FIRST_DIR_OPEN = 1
    FIRST_BUILD_START = 2
    FIRST_BUILD_DONE = 4
    FORT_CREATED = 8
    BASE_DAMAGED = 16
    BASE_DESTROYED = 32
    PLANNED_INFO_LOADED = 64
    IS_SUSPENDED = BASE_DAMAGED | BASE_DESTROYED


FORT_STATE_NAMES = buildNamesDict(FORT_STATE)

class FORT_CONTRIBUTION_TYPE():
    CLIENT = 0
    SORTIE_BASE = 100
    BATTLE_BASE = 200


class FORT_ATTACK_RESULT():
    DRAW = 0
    BUILDINGS_CAPTURED_MASK = 3
    BASE_CAPTURED_FLAG = 16
    PLANNED = 100
    IN_PROGRESS = 101
    RESULTS_LOST = 102
    SKIPPED = 103
    FAILED_TO_START = 104
    TECHNICAL_DRAW = 105
    FAILED_TO_SCHEDULE = 106
    SPECIAL_RESULTS = (PLANNED,
     IN_PROGRESS,
     RESULTS_LOST,
     SKIPPED,
     FAILED_TO_START,
     TECHNICAL_DRAW,
     FAILED_TO_SCHEDULE)


class FORT_ATK_IDX():
    ENEMY_DBID = 0
    ENEMY_ABBREV = 1
    ENEMY_DIR = 2
    BATTLE_ID = 3
    ATK_LEVEL = 4
    DEF_LEVEL = 5
    DIVISION = 6
    PERIPHERY = 7
    ATTACK_RESULT = -2
    ATTACK_RESOURCE = -1


class DELETE_BATTLE_REASON():
    UNKNOWN = 0
    ADMIN_REQUEST = 1
    BASE_DAMAGED = 2
    DEFENCE_SHUTDOWN = 3
    DIR_CLOSED = 4
    FORT_DELETED = 5
    NO_ATTACK_INFO = 6


class FORT_CLIENT_METHOD():
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
    SHUTDOWN_DEF_HOUR = 24
    CANCEL_SHUTDOWN = 25
    DMG_BUILDING = 26
    GET_ENEMY_CLAN_CARD = 27
    PLAN_ATTACK = 28
    DELETE_PLANNED_BATTLES = 29
    CHANGE_ATTACK_RESULT = 30
    CREATE_JOIN_FORT_BATTLE = 31
    SCHEDULE_FORT_BATTLE = 32
    GET_FORT_BATTLE_DATA = 33
    ADD_FAVORITE = 34
    REMOVE_FAVORITE = 35
    ACTIVATE_CONSUMABLE = 36
    DEACTIVATE_CONSUMABLE = 37
    DEBUG_UNLOCK_DIR = 38


CLAN_LEADER = CLAN_MEMBER_FLAGS.LEADER
CLAN_OFFICERS = CLAN_MEMBER_FLAGS.LEADER | CLAN_MEMBER_FLAGS.VICE_LEADER
CLAN_ANY_MEMBERS = 0
_FORT_CLIENT_METHOD_ROLES = {FORT_CLIENT_METHOD.CREATE: CLAN_LEADER,
 FORT_CLIENT_METHOD.DELETE: CLAN_LEADER,
 FORT_CLIENT_METHOD.CHANGE_DEF_HOUR: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.SHUTDOWN_DEF_HOUR: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.CANCEL_SHUTDOWN: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.CHANGE_VACATION: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.CHANGE_PERIPHERY: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.CHANGE_OFF_DAY: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.OPEN_DIR: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.CLOSE_DIR: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.ADD_BUILDING: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.DEL_BUILDING: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.UPGRADE: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.ADD_ORDER: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.ACTIVATE_ORDER: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.TRANSPORT: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.ADD_FAVORITE: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.REMOVE_FAVORITE: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.PLAN_ATTACK: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.ATTACH: CLAN_ANY_MEMBERS,
 FORT_CLIENT_METHOD.KEEPALIVE: CLAN_ANY_MEMBERS,
 FORT_CLIENT_METHOD.GET_ENEMY_CLAN_CARD: CLAN_ANY_MEMBERS,
 FORT_CLIENT_METHOD.CREATE_JOIN_FORT_BATTLE: CLAN_ANY_MEMBERS,
 FORT_CLIENT_METHOD.CREATE_SORTIE: CLAN_ANY_MEMBERS,
 FORT_CLIENT_METHOD.GET_SORTIE_DATA: CLAN_ANY_MEMBERS,
 FORT_CLIENT_METHOD.ACTIVATE_CONSUMABLE: CLAN_ANY_MEMBERS,
 FORT_CLIENT_METHOD.DEACTIVATE_CONSUMABLE: CLAN_ANY_MEMBERS,
 FORT_CLIENT_METHOD.SET_DEV_MODE: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.ADD_TIME_SHIFT: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.SCHEDULE_FORT_BATTLE: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.DELETE_PLANNED_BATTLES: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.CHANGE_ATTACK_RESULT: CLAN_OFFICERS,
 FORT_CLIENT_METHOD.CONTRIBUTE: CLAN_ANY_MEMBERS,
 FORT_CLIENT_METHOD.DMG_BUILDING: CLAN_ANY_MEMBERS,
 FORT_CLIENT_METHOD.DEBUG_UNLOCK_DIR: CLAN_OFFICERS}

def makeDirPosByte(dir, pos):
    return dir << 4 | pos


def parseDirPosByte(dirPosByte):
    return (dirPosByte >> 4 & 15, dirPosByte & 15)


class BuildingDescr():
    FORMAT_HEADER = '<BBBbiiii'
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
            self.orderInProduction = {'count': abs(productionCount),
             'timeFinish': productionTimeFinish,
             'isSuspended': bool(productionCount < 0)}
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
        attachedCount = len(self.attachedPlayers)
        timeFinish = orderInProduction.get('timeFinish', 0)
        productionCount = orderInProduction.get('count', 0)
        if orderInProduction.get('isSuspended', False):
            productionCount = -productionCount
        format = '%dq' % attachedCount
        compactDescr = struct.pack((self.FORMAT_HEADER + format), self.typeID, self.level, dirPosByte, productionCount, timeFinish, resourceCount, self.timeTransportCooldown, attachedCount, *list(self.attachedPlayers))
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

    def isProductionSuspended(self):
        inProduction = self.orderInProduction
        if not inProduction:
            return False
        return inProduction.get('isSuspended', False)

    def buildingStatus(self):
        minLevel = fortified_regions.g_cache.defenceConditions.minRegionLevel
        if self.level < minLevel:
            return FORT_BUILDING_STATUS.LOW_LEVEL
        if self.hp < self.levelRef.hp * FORT_BATTLE_BUILDING_HP_PERCENT / 100:
            return FORT_BUILDING_STATUS.DESTROYED
        return FORT_BUILDING_STATUS.READY_FOR_BATTLE

    def getFortBattleResourceToCapture(self):
        return self.levelRef.hp * FORT_BATTLE_BUILDING_HP_PERCENT / 100

    def __repr__(self):
        return '[%s] t=%s, l=%s, hp=%s/%s, stor=%s/%s, pos=%s:%s, tCD=%s, inProd=%s(%s), attach=%s' % (FORT_BUILDING_TYPE_NAMES.get(self.typeID, ''),
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


class FortifiedRegionBase(OpsUnpacker):
    _opsFormatDefs = initOpsFormatDef({FORT_OP.CREATE_NEW: ('qqi',
                          '_createNew',
                          'L',
                          [('i', 'q')]),
     FORT_OP.DELETE: ('q', '_delete'),
     FORT_OP.ADD_BUILDING: ('BBB', '_addBuilding'),
     FORT_OP.DEL_BUILDING: ('B', '_delBuilding'),
     FORT_OP.CONTRIBUTE: ('qBii', '_contribute'),
     FORT_OP.ACTIVATE_ORDER: ('Biiiiq', '_activateOrder'),
     FORT_OP.REPLACE_CONSUMABLES: ('qHqiii',
                                   '_replaceConsumables',
                                   'N',
                                   [('H', 'Bii')]),
     FORT_OP.CHANGE_ORDER_COUNT: ('Bii', '_changeOrderCount'),
     FORT_OP.SET_UNIT_MGR_IS_DEAD: ('qH', '_setUnitMgrIsDead'),
     FORT_OP.DELETE_CONSUMABLES: ('qH', '_deleteConsumables'),
     FORT_OP.ACTIVATE_DEF_HOUR: ('Bq', '_activateDefHour'),
     FORT_OP.CHANGE_DEF_HOUR: ('Biiq', '_changeDefHour'),
     FORT_OP.CHANGE_PERIPHERY: ('Hi', '_changePeriphery'),
     FORT_OP.CHANGE_OFF_DAY: ('biiq', '_changeOffDay'),
     FORT_OP.CHANGE_VACATION: ('iiiq', '_changeVacation'),
     FORT_OP.EXPIRE_EVENT: ('Bi', '_expireEvent'),
     FORT_OP.SET_DEV_MODE: ('B', '_setDevMode'),
     FORT_OP.SET_TIME_SHIFT: ('i', '_setTimeShift'),
     FORT_OP.OPEN_DIR: ('Biq', '_openDir'),
     FORT_OP.CLOSE_DIR: ('B', '_closeDir'),
     FORT_OP.ADD_SORTIE: ('qqBHHBBii',
                          '_setSortie',
                          'SS',
                          ['', '']),
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
     FORT_OP.SHUTDOWN_DEF_HOUR: ('iq', '_shutdownDefHour'),
     FORT_OP.ADD_EVENT: ('Biiq', '_addEvent'),
     FORT_OP.CANCEL_EVENT: ('B', '_cancelEvent'),
     FORT_OP.DMG_BUILDING: ('Biq', '_dmgBuilding'),
     FORT_OP.SUSPEND_PRODUCTION: ('Bi', '_suspendProduction'),
     FORT_OP.RESUME_PRODUCTION: ('Bi', '_resumeProduction'),
     FORT_OP.ENEMY_CLAN_CARD: ('qBBbbiiiibb',
                               '_onEnemyClanCard',
                               'SSSSSMND',
                               ['',
                                '',
                                '',
                                '',
                                '',
                                ('B', 'BBBi', ('level', 'dirPosByte', 'hp')),
                                ('i', 'iBq11p'),
                                ('B', 'B', 'i')]),
     FORT_OP.DELETE_BATTLES_BY_TIME: ('iibb', '_deleteBattlesByTime'),
     FORT_OP.DELETE_BATTLES_BY_CLAN: ('qiibb', '_deleteBattlesByClan'),
     FORT_OP.ADD_ATTACK: ('iBBqqBBBHbi',
                          '_addAttack',
                          'S',
                          ['']),
     FORT_OP.ADD_DEFENCE: ('iBBqqBBBbi',
                           '_addDefence',
                           'S',
                           ['']),
     FORT_OP.SET_LOCKED_DIRS: ('B', '_setLockedDirMask'),
     FORT_OP.SET_ATTACK_RESULT: ('biqBi', '_setAttackResult'),
     FORT_OP.ADD_FORT_BATTLE: ('qBiqqBB', '_addFortBattle'),
     FORT_OP.REMOVE_FORT_BATTLE: ('q', '_removeFortBattle'),
     FORT_OP.SET_FORT_BATTLE_BUILDNUM: ('qbi', '_setFortBattleBuildnum'),
     FORT_OP.SET_FORT_BATTLE_RESULTS: ('qb', '_setFortBattleResults'),
     FORT_OP.SET_FORT_BATTLE_DIRECTIONS: ('q',
                                          '_setFortBattleDirections',
                                          'S',
                                          ['']),
     FORT_OP.FORT_BATTLE_UNIT: ('', '_unpackFortBattleUnit'),
     FORT_OP.SET_ENEMY_READY_FOR_BATTLE: ('qB', '_setEnemyReadyForBattle'),
     FORT_OP.REMOVE_FORT_BATTLE_UNIT: ('q', '_removeFortBattleUnit'),
     FORT_OP.SET_FORT_BATTLE_ROUND: ('qB', '_setFortBattleRound'),
     FORT_OP.ADD_FAVORITE: ('q', '_addFavorite'),
     FORT_OP.REMOVE_FAVORITE: ('q', '_removeFavorite'),
     FORT_OP.SET_BUILD_MAPS: ('BiHH', '_setBuildingMaps'),
     FORT_OP.EMERGENCY_ON_RESTORE: ('', '_onEmergencyRestore'),
     FORT_OP.DELETE_BATTLE_BY_ID: ('qb', '_deleteBattleByID'),
     FORT_OP.ADD_INFLUENCE_POINTS: ('i', '_addInfluencePoints'),
     FORT_OP.SET_RESOURCE: ('Bi', '_setBuildingResource'),
     FORT_OP.SET_DEF_HOUR: ('i', '_setDefHour'),
     FORT_OP.SET_OFF_DAY: ('i', '_setOffDay'),
     FORT_OP.SET_VACATION: ('ii', '_setVacation'),
     FORT_OP.SET_PERIPHERY: ('H', '_setPeriphery'),
     FORT_OP.SET_INFLUENCE_POINTS: ('i', '_setInfluencePoints')})
    FORMAT_HEADER = '<qiiiiiHBbbBBBBBBBBBBBHHHHHq'
    SIZE_HEADER = struct.calcsize(FORMAT_HEADER)
    FORMAT_EVENT = '<BIqq'
    SIZE_EVENT = struct.calcsize(FORMAT_EVENT)
    FORMAT_BUILDING_HEADER = '<BH'
    SIZE_BUILDING_HEADER = struct.calcsize(FORMAT_BUILDING_HEADER)
    FORMAT_ORDER = '<BBh'
    SIZE_ORDER = struct.calcsize(FORMAT_ORDER)
    FORMAT_CONTRIBUTION_HEADER = '<qb'
    SIZE_CONTRIBUTION_HEADER = struct.calcsize(FORMAT_CONTRIBUTION_HEADER)
    FORMAT_CONTRIBUTION_ITEM = '<ii'
    SIZE_CONTRIBUTION_ITEM = struct.calcsize(FORMAT_CONTRIBUTION_ITEM)
    FORMAT_ADD_SORTIE_HEADER = '<qqBHHBBii'
    SIZE_ADD_SORTIE_HEADER = struct.calcsize(FORMAT_ADD_SORTIE_HEADER)
    FORMAT_ADD_CONSUMABLE_HEADER = '<qH'
    SIZE_ADD_CONSUMABLE_HEADER = struct.calcsize(FORMAT_ADD_CONSUMABLE_HEADER)
    FORMAT_ADD_CONSUMABLE_META_HEADER = '<qqqBBH'
    SIZE_ADD_CONSUMABLE_META_HEADER = struct.calcsize(FORMAT_ADD_CONSUMABLE_META_HEADER)
    FORMAT_SORTIE_UNIT_HEADER = '<qH'
    SIZE_SORTIE_UNIT_HEADER = struct.calcsize(FORMAT_SORTIE_UNIT_HEADER)
    FORMAT_ADD_BATTLE_HEADER = '<qBBibbqqBiBBB'
    SIZE_ADD_BATTLE_HEADER = struct.calcsize(FORMAT_ADD_BATTLE_HEADER)
    FORMAT_ADD_BATTLEUNIT_HEADER = '<qh'
    SIZE_ADD_BATTLEUNIT_HEADER = struct.calcsize(FORMAT_ADD_BATTLEUNIT_HEADER)
    FORMAT_ATTACK_HEADER = '<iBBqqBBBHbi'
    SIZE_ATTACK_HEADER = struct.calcsize(FORMAT_ATTACK_HEADER)
    FORMAT_DEFENCE_HEADER = '<iBBqqBBBbi'
    SIZE_DEFENCE_HEADER = struct.calcsize(FORMAT_DEFENCE_HEADER)
    FORMAT_FORT_BATTLE_UNIT_HEADER = '<q'
    SIZE_FORT_BATTLE_UNIT_HEADER = struct.calcsize(FORMAT_FORT_BATTLE_UNIT_HEADER)

    def __init__(self):
        self.statistics = None
        self._empty()
        return

    def _persist(self):
        pass

    def isEmpty(self):
        return self.dbID == 0

    def isSuspended(self):
        return self.dbID and self.state & FORT_STATE.IS_SUSPENDED

    def isLoaded(self):
        return not self.dbID or self.state & FORT_STATE.PLANNED_INFO_LOADED != 0

    def _empty(self):
        self.dbID = 0
        self._packed = EMPTY_FORT_PACK
        self._dirty = False

    def _getTime(self):
        return int(time.time()) + self._debugTimeShift

    def __repr__(self):
        if not self.dbID:
            return 'Fort: empty'
        s = 'Fort:\n ID=%s, p=%s, l=%s, s=%x, dM=%x, lD=%x, dH=%s, oD=%s, v=%s/%s, _D=%s, t+=%s(%s), ip =%s, c=%s\n ev=%s\n buildings(%s)' % (self.dbID,
         self.peripheryID,
         self.level,
         self.state,
         self.dirMask,
         self.lockedDirMask,
         self.defenceHour,
         self.offDay,
         self.vacationStart,
         self.vacationFinish,
         self._devMode,
         self._debugTimeShift,
         time.ctime(time.time() + self._debugTimeShift),
         self.influencePoints,
         self.creatorDBID,
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

        if self.sorties:
            s += '\n sorties(%s)' % len(self.sorties)
            for key, args in self.sorties.iteritems():
                s += '\n  [%s] %s' % (key, args)

        if self.consumables:
            s += '\n consumables(%s)' % len(self.consumables)
            for key, args in self.consumables.iteritems():
                s += '\n  [%s] %s' % (key, args)

        if self.battles:
            s += '\n battles(%s)' % len(self.battles)
            for key, args in self.battles.iteritems():
                s += '\n  [%s] %s' % (key, args)

        if self.battleUnits:
            s += '\n battleUnits(%s)' % len(self.battleUnits)
        if self.attacks:
            s += '\n attacks(%s)' % len(self.attacks)
            for key, args in self.attacks.iteritems():
                s += '\n  [%s] %s %s' % (key, args, time.ctime(key[0]))

        if self.defences:
            s += '\n defences(%s)' % len(self.defences)
            for key, args in self.defences.iteritems():
                s += '\n  [%s] %s %s' % (key, args, time.ctime(key[0]))

        if self.favorites:
            s += '\n favorites(%s)' % len(self.favorites) + '\n  ' + repr(self.favorites)
        return s

    def pack(self, isForced = False):
        if not self._dirty and not isForced:
            return self._packed
        self._dirty = False
        if self.dbID:
            statistics = self.statistics.makeCompDescr()
            packed = struct.pack(self.FORMAT_HEADER, self.dbID, self.peripheryID, self.vacationStart, self.vacationFinish, self._debugTimeShift, self.influencePoints, self.state, self.level, self.defenceHour, self.offDay, self._devMode, self.dirMask, self.lockedDirMask, len(self.events), len(self.buildings), len(self.orders), len(self.battles), len(self.battleUnits), len(self.sorties), len(self.consumables), len(self.consumablesMeta), len(self.playerContributions), len(statistics), len(self.attacks), len(self.defences), len(self.favorites), self.creatorDBID)
            for eventType, (unixtime, eventValue, initiatorDBID) in self.events.iteritems():
                packed += struct.pack(self.FORMAT_EVENT, eventType, unixtime, eventValue, initiatorDBID)

            for buildTypeID, buildingCompactDescr in self.buildings.iteritems():
                packed += struct.pack(self.FORMAT_BUILDING_HEADER, buildTypeID, len(buildingCompactDescr))
                packed += buildingCompactDescr

            fmt = self.FORMAT_ORDER
            for orderTypeID, (count, level) in self.orders.iteritems():
                packed += struct.pack(fmt, orderTypeID, level, count)

            fmt = self.FORMAT_ATTACK_HEADER
            for (timeAttack, dirFrom), (defenderClanDBID, defenderClanAbbrev, dirTo, battleID, attackerFortLevel, defenderFortLevel, division, peripheryID, attackResult, attackResource) in self.attacks.iteritems():
                packed += struct.pack(fmt, timeAttack, dirFrom, dirTo, defenderClanDBID, battleID, attackerFortLevel, defenderFortLevel, division, peripheryID, attackResult, attackResource)
                packed += packPascalString(defenderClanAbbrev)

            fmt = self.FORMAT_DEFENCE_HEADER
            for (timeAttack, dirTo), (attackerClanDBID, attackerClanAbbrev, dirFrom, battleID, attackerFortLevel, defenderFortLevel, division, attackResult, attackResource) in self.defences.iteritems():
                packed += struct.pack(fmt, timeAttack, dirFrom, dirTo, attackerClanDBID, battleID, attackerFortLevel, defenderFortLevel, division, attackResult, attackResource)
                packed += packPascalString(attackerClanAbbrev)

            fmt = self.FORMAT_ADD_SORTIE_HEADER
            for (unitMgrID, peripheryID), rec in self.sorties.iteritems():
                cmdrDBID, rosterTypeID, state, count, maxCount, timestamp, igrType, cmdrName, strComment = rec
                packed += struct.pack(fmt, unitMgrID, cmdrDBID, rosterTypeID, state, peripheryID, count, maxCount, timestamp, igrType)
                packed += packPascalString(cmdrName)
                packed += packPascalString(strComment)

            fmt = self.FORMAT_ADD_CONSUMABLE_HEADER
            for (unitMgrID, peripheryID), rec in self.consumables.iteritems():
                packed += struct.pack(fmt, unitMgrID, peripheryID)
                packed += packPascalString(cPickle.dumps(rec, -1))

            fmt = self.FORMAT_ADD_CONSUMABLE_META_HEADER
            for (unitMgrID, peripheryID), rec in self.consumablesMeta.iteritems():
                expireTime, prebattleType, isAlive, rev = rec
                packed += struct.pack(fmt, unitMgrID, expireTime, rev, prebattleType, isAlive, peripheryID)

            fmt = self.FORMAT_ADD_BATTLE_HEADER
            for battleID, data in self.battles.iteritems():
                direction = data['direction']
                isDefence = data['isDefence']
                attackTime = data['attackTime']
                prevBuildNum = data['prevBuildNum']
                currentBuildNum = data['currentBuildNum']
                attackerClanDBID = data['attackerClanDBID']
                defenderClanDBID = data['defenderClanDBID']
                isEnemyReadyForBattle = data['isEnemyReadyForBattle']
                canUseEquipments = data['canUseEquipments']
                division = data['division']
                roundStart = data.get('roundStart', 0)
                isBattleRound = data.get('isBattleRound', False)
                attackerBuildList = packPascalString(cPickle.dumps(data['attackerBuildList'], -1))
                defenderBuildList = packPascalString(cPickle.dumps(data['defenderBuildList'], -1))
                attackerFullBuildList = packPascalString(cPickle.dumps(data['attackerFullBuildList'], -1))
                defenderFullBuildList = packPascalString(cPickle.dumps(data['defenderFullBuildList'], -1))
                battleResultList = packPascalString(cPickle.dumps(data['battleResultList'], -1))
                packed += struct.pack(fmt, battleID, direction, isDefence, attackTime, prevBuildNum, currentBuildNum, attackerClanDBID, defenderClanDBID, isEnemyReadyForBattle, roundStart, isBattleRound, canUseEquipments, division)
                packed += attackerBuildList
                packed += defenderBuildList
                packed += attackerFullBuildList
                packed += defenderFullBuildList
                packed += battleResultList

            fmt = self.FORMAT_ADD_BATTLEUNIT_HEADER
            for battleID, unitStr in self.battleUnits.iteritems():
                packed += struct.pack(fmt, battleID, len(unitStr))
                packed += unitStr

            fmtHdr = self.FORMAT_CONTRIBUTION_HEADER
            fmtItem = self.FORMAT_CONTRIBUTION_ITEM
            for accountDBID, accDict in self.playerContributions.iteritems():
                packed += struct.pack(fmtHdr, accountDBID, len(accDict))
                for datestamp, resCount in accDict.iteritems():
                    packed += struct.pack(fmtItem, datestamp, resCount)

            packed += statistics
            fmt = '<%dq' % len(self.favorites)
            packed += struct.pack(fmt, *list(self.favorites))
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
        self.dbID, self.peripheryID, self.vacationStart, self.vacationFinish, self._debugTimeShift, self.influencePoints, self.state, self.level, self.defenceHour, self.offDay, self._devMode, self.dirMask, self.lockedDirMask, lenEvents, lenBuildings, lenOrders, lenBattles, lenBattleUnits, lenSorties, lenConsumables, lenConsumablesMeta, lenPlayerContributions, lenStatistics, lenPlannedAttacks, lenPlannedDefences, lenFavorites, self.creatorDBID = struct.unpack_from(self.FORMAT_HEADER, packed)
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
            self._unpackBuilding(buildingCompactDescr, buildTypeID)
            offset += lenDescr

        sz = self.SIZE_ORDER
        fmt = self.FORMAT_ORDER
        self.orders = {}
        for i in xrange(lenOrders):
            orderTypeID, level, count = struct.unpack_from(fmt, packed, offset)
            self.orders[orderTypeID] = (count, level)
            offset += sz

        fmt = self.FORMAT_ATTACK_HEADER
        sz = self.SIZE_ATTACK_HEADER
        self.attacks = {}
        self._lastAttacks = {}
        for i in xrange(lenPlannedAttacks):
            timeAttack, dirFrom, dirTo, defenderClanDBID, battleID, atkFortLevel, defFortLevel, division, peripheryID, attackResult, attackResource = struct.unpack_from(fmt, packed, offset)
            clanAbbrev, lenClanAbbrev = unpackPascalString(packed, offset + sz)
            self.attacks[timeAttack, dirFrom] = (defenderClanDBID,
             clanAbbrev,
             dirTo,
             battleID,
             atkFortLevel,
             defFortLevel,
             division,
             peripheryID,
             attackResult,
             attackResource)
            lastTime = self._lastAttacks.get(defenderClanDBID, 0)
            if timeAttack > lastTime:
                self._lastAttacks[defenderClanDBID] = timeAttack
            offset += sz + lenClanAbbrev

        fmt = self.FORMAT_DEFENCE_HEADER
        sz = self.SIZE_DEFENCE_HEADER
        self.defences = {}
        for i in xrange(lenPlannedDefences):
            timeAttack, dirFrom, dirTo, attackerClanDBID, battleID, atkFortLevel, defFortLevel, division, attackResult, attackResource = struct.unpack_from(fmt, packed, offset)
            clanAbbrev, lenClanAbbrev = unpackPascalString(packed, offset + sz)
            self.defences[timeAttack, dirTo] = (attackerClanDBID,
             clanAbbrev,
             dirFrom,
             battleID,
             atkFortLevel,
             defFortLevel,
             division,
             attackResult,
             attackResource)
            offset += sz + lenClanAbbrev

        sz = self.SIZE_ADD_SORTIE_HEADER
        fmt = self.FORMAT_ADD_SORTIE_HEADER
        self.sorties = {}
        self._sortieUnits = {}
        for i in xrange(lenSorties):
            unitMgrID, cmdrDBID, rosterTypeID, state, peripheryID, count, maxCount, timestamp, igrType = struct.unpack_from(fmt, packed, offset)
            cmdrName, lenCmdrName = unpackPascalString(packed, offset + sz)
            strComment, lenComment = unpackPascalString(packed, offset + sz + lenCmdrName)
            sortieKey = (unitMgrID, peripheryID)
            self.sorties[sortieKey] = (cmdrDBID,
             rosterTypeID,
             state,
             count,
             maxCount,
             timestamp,
             igrType,
             cmdrName,
             strComment)
            offset += sz + lenCmdrName + lenComment

        sz = self.SIZE_ADD_CONSUMABLE_HEADER
        fmt = self.FORMAT_ADD_CONSUMABLE_HEADER
        self.consumables = {}
        for i in xrange(lenConsumables):
            unitMgrID, peripheryID = struct.unpack_from(fmt, packed, offset)
            strConsumablesList, lenConsumablesList = unpackPascalString(packed, offset + sz)
            rec = cPickle.loads(strConsumablesList)
            self.consumables[unitMgrID, peripheryID] = rec
            offset += sz + lenConsumablesList

        sz = self.SIZE_ADD_CONSUMABLE_META_HEADER
        fmt = self.FORMAT_ADD_CONSUMABLE_META_HEADER
        self.consumablesMeta = {}
        for i in xrange(lenConsumablesMeta):
            unitMgrID, expireTime, rev, prebattleType, isAlive, peripheryID = struct.unpack_from(fmt, packed, offset)
            self.consumablesMeta[unitMgrID, peripheryID] = (expireTime,
             prebattleType,
             isAlive,
             rev)
            offset += sz

        sz = self.SIZE_ADD_BATTLE_HEADER
        fmt = self.FORMAT_ADD_BATTLE_HEADER
        self.battles = {}
        for i in xrange(lenBattles):
            battleID, direction, isDefence, attackTime, prevBuildNum, currentBuildNum, attackerClanDBID, defenderClanDBID, isEnemyReadyForBattle, roundStart, isBattleRound, canUseEquipments, division = struct.unpack_from(fmt, packed, offset)
            attackerBuildListStr, attackerListLen = unpackPascalString(packed, offset + sz)
            attackerBuildList = cPickle.loads(attackerBuildListStr)
            defenderBuildListStr, defenderListLen = unpackPascalString(packed, offset + sz + attackerListLen)
            defenderBuildList = cPickle.loads(defenderBuildListStr)
            attackerFullBuildListStr, attackerFullListLen = unpackPascalString(packed, offset + sz + attackerListLen + defenderListLen)
            attackerFullBuildList = cPickle.loads(attackerFullBuildListStr)
            defenderFullBuildListStr, defenderFullListLen = unpackPascalString(packed, offset + sz + attackerListLen + defenderListLen + attackerFullListLen)
            defenderFullBuildList = cPickle.loads(defenderFullBuildListStr)
            battleResultListStr, battleResultListLen = unpackPascalString(packed, offset + sz + attackerListLen + defenderListLen + attackerFullListLen + defenderFullListLen)
            battleResultList = cPickle.loads(battleResultListStr)
            offset += sz + attackerListLen + defenderListLen + attackerFullListLen + defenderFullListLen + battleResultListLen
            self.battles[battleID] = {'direction': direction,
             'isDefence': bool(isDefence),
             'attackTime': attackTime,
             'attackerClanDBID': attackerClanDBID,
             'defenderClanDBID': defenderClanDBID,
             'attackerBuildList': attackerBuildList,
             'defenderBuildList': defenderBuildList,
             'attackerFullBuildList': attackerFullBuildList,
             'defenderFullBuildList': defenderFullBuildList,
             'battleResultList': battleResultList,
             'prevBuildNum': prevBuildNum,
             'currentBuildNum': currentBuildNum,
             'isEnemyReadyForBattle': isEnemyReadyForBattle,
             'roundStart': roundStart,
             'isBattleRound': isBattleRound,
             'canUseEquipments': canUseEquipments,
             'division': division}

        sz = self.SIZE_ADD_BATTLEUNIT_HEADER
        fmt = self.FORMAT_ADD_BATTLEUNIT_HEADER
        self.battleUnits = {}
        for i in xrange(lenBattleUnits):
            battleID, unitStrLen = struct.unpack_from(fmt, packed, offset)
            offset += sz
            unitStr = packed[offset:offset + unitStrLen]
            offset += unitStrLen
            self.battleUnits[battleID] = unitStr

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
        fmt = '<%dq' % lenFavorites
        self.favorites = set(struct.unpack_from(fmt, packed, offset))
        offset += struct.calcsize(fmt)
        raise offset == len(packed) or AssertionError

    def _unpackBuilding(self, buildingCompactDescr, buildTypeID):
        building = BuildingDescr(buildingCompactDescr)
        dirPos = makeDirPosByte(building.direction, building.position)
        self._dirPosToBuildType[dirPos] = buildTypeID
        for accountDBID in building.attachedPlayers:
            self._playerAttachments[accountDBID] = buildTypeID

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
         self._debugTimeShift,
         self.influencePoints,
         self.creatorDBID,
         self.lockedDirMask), buildings=self.buildings, orders=self.orders, events=self.events, playerContributions=self.playerContributions, battles=self.battles, statistics=self.statistics.makeCompDescr(), favorites=self.favorites, consumables=self.consumables, consumablesMeta=self.consumablesMeta)
        return pdata

    def deserialize(self, pdata):
        if not isinstance(pdata, dict) or not pdata:
            self._empty()
            return
        self.dbID = pdata['dbID']
        self._dirty = True
        if self.dbID:
            self.statistics = dossiers2.getFortifiedRegionsDossierDescr(pdata['statistics'])
            self.level, self.state, self.dirMask, self.peripheryID, self.defenceHour, self.offDay, self.vacationStart, self.vacationFinish, self._devMode, self._debugTimeShift, self.influencePoints, self.creatorDBID, self.lockedDirMask = pdata['attrs']
            self.buildings = pdata['buildings']
            self.orders = pdata['orders']
            self.events = pdata['events']
            self.playerContributions = pdata['playerContributions']
            self.favorites = pdata['favorites']
            self.sorties = {}
            self.consumables = pdata['consumables']
            self.consumablesMeta = pdata['consumablesMeta']
            self._sortieUnits = {}
            self.battles = pdata['battles']
            self.battleUnits = {}
            self.attacks = {}
            self.defences = {}
            self._lastAttacks = {}
            self._dirPosToBuildType = {}
            self._playerAttachments = {}
            for buildTypeID, buildingCompactDescr in self.buildings.iteritems():
                self._unpackBuilding(buildingCompactDescr, buildTypeID)

            self.state |= FORT_STATE.FORT_CREATED
            for eventID in self.events.keys():
                args = self.events.get(eventID)
                timestamp = args[0]
                if timestamp < INT_MIN or timestamp > INT_MAX:
                    LOG_WARNING('Removing bad event timestamp', self.dbID, eventID, args)
                    self.events.pop(eventID)

        try:
            self.pack()
        except Exception as e:
            LOG_CURRENT_EXCEPTION()
            LOG_VLK('FortifiedRegionBase.self: %s' % repr(self))
            raise e

    def getBuilding(self, buildingTypeID):
        buildCompDescr = self.buildings.get(buildingTypeID)
        if buildCompDescr:
            return BuildingDescr(buildCompDescr)
        else:
            return None

    def setBuilding(self, buildingTypeID, buildingDescr):
        self.buildings[buildingTypeID] = buildingDescr.makeCompactDescr()

    def getBuildingMaps(self, buildingTypeID):
        return self.events.get(FORT_EVENT_TYPE.BUILDING_MAPS_BASE + buildingTypeID, (0, 0, 0))

    def setBuildingMaps(self, buildingTypeID, nextMapTimestamp, nextMapID, curMapID):
        self._setBuildingMaps(buildingTypeID, nextMapTimestamp, nextMapID, curMapID)
        self._dirty = True

    def rollBuildingMapID(self):
        return random.sample(fortified_regions.g_cache.fortBattleMaps, 1)[0]

    def isValidBuildingMapID(self, mapGeometryID):
        return mapGeometryID in fortified_regions.g_cache.fortBattleMaps

    def validateBuildingMaps(self):
        minLevel = fortified_regions.g_cache.defenceConditions.minRegionLevel
        for buildTypeID in self.buildings.iterkeys():
            building = self.getBuilding(buildTypeID)
            eventTypeID = FORT_EVENT_TYPE.BUILDING_MAPS_BASE + buildTypeID
            if self.defenceHour != NOT_ACTIVATED and building.level >= minLevel:
                nextMapTimestamp, nextMapID, curMapID = self.getBuildingMaps(buildTypeID)
                isCurrentValid = self.isValidBuildingMapID(curMapID)
                isNextValid = self.isValidBuildingMapID(nextMapID)
                if not isCurrentValid or not isNextValid:
                    mapList = [self.rollBuildingMapID(), self.rollBuildingMapID()]
                    if isNextValid:
                        mapList.append(nextMapID)
                    if isCurrentValid:
                        mapList.append(curMapID)
                    LOG_DEBUG_DEV('validateBuildingMaps', buildTypeID, curMapID, isCurrentValid, nextMapID, isNextValid, mapList)
                    nextMapID, curMapID = mapList[-2:]
                    nextMapTimestamp = self._getTime() + fortified_regions.g_cache.mapCooldownTime
                    self.setBuildingMaps(buildTypeID, nextMapTimestamp, nextMapID, curMapID)
            elif eventTypeID in self.events:
                self._cancelEvent(eventTypeID)
                self._dirty = True

    def _setBuildingMaps(self, buildingTypeID, nextMapTimestamp, nextMapID, curMapID):
        LOG_DEBUG_DEV('_setBuildingMaps', buildingTypeID, nextMapTimestamp, nextMapID, curMapID)
        self.events[FORT_EVENT_TYPE.BUILDING_MAPS_BASE + buildingTypeID] = (nextMapTimestamp, nextMapID, curMapID)
        self.storeOp(FORT_OP.SET_BUILD_MAPS, buildingTypeID, nextMapTimestamp, nextMapID, curMapID)

    def validateDefHour(self, value, forbiddenDefenseHours = (), isAdmin = False):
        if value < -1 or value == -1 and isAdmin == False or value > 23 or value in forbiddenDefenseHours:
            return FORT_ERROR.BAD_HOUR_VALUE
        if IS_KOREA and value >= 15 and value <= 21:
            return FORT_ERROR.CURFEW_HOUR
        return OK

    def validateOffDay(self, value):
        if value < -1 or value > 6:
            return FORT_ERROR.BAD_DAY_VALUE
        return OK

    def _broadcastFortSystemMessage(self, fortEvent, **kwargs):
        pass

    def _changeEncounterValue(self, timeAttack, dir, encounters, chgClanDBID, fortAtkIdx, value):
        key = (timeAttack, dir)
        args = encounters[key]
        enemyClanDBID = args[FORT_ATK_IDX.ENEMY_DBID]
        if enemyClanDBID == chgClanDBID:
            args = list(args)
            args[fortAtkIdx] = value
            if encounters == self.attacks:
                self._addAttack(timeAttack, dir, args[FORT_ATK_IDX.ENEMY_DIR], args[FORT_ATK_IDX.ENEMY_DBID], args[FORT_ATK_IDX.BATTLE_ID], args[FORT_ATK_IDX.ATK_LEVEL], args[FORT_ATK_IDX.DEF_LEVEL], args[FORT_ATK_IDX.DIVISION], args[FORT_ATK_IDX.PERIPHERY], args[FORT_ATK_IDX.ATTACK_RESULT], args[FORT_ATK_IDX.ATTACK_RESOURCE], args[FORT_ATK_IDX.ENEMY_ABBREV])
            else:
                self._addDefence(timeAttack, dir, args[FORT_ATK_IDX.ENEMY_DIR], args[FORT_ATK_IDX.ENEMY_DBID], args[FORT_ATK_IDX.BATTLE_ID], args[FORT_ATK_IDX.ATK_LEVEL], args[FORT_ATK_IDX.DEF_LEVEL], args[FORT_ATK_IDX.DIVISION], args[FORT_ATK_IDX.ATTACK_RESULT], args[FORT_ATK_IDX.ATTACK_RESOURCE], args[FORT_ATK_IDX.ENEMY_ABBREV])
        else:
            LOG_WARNING('_changeEncounterValue: WRONG args', timeAttack, dir, encounters, chgClanDBID, enemyClanDBID, fortAtkIdx, value)

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

    def _rebuildLastAttackIndexes(self):
        self._lastAttacks = {}
        for (attackTime, dirFrom), args in self.attacks.iteritems():
            clanDBID = args[FORT_ATK_IDX.ENEMY_DBID]
            lastTime = self._lastAttacks.get(clanDBID, 0)
            if attackTime > lastTime:
                self._lastAttacks[clanDBID] = attackTime

    def getPlayerContributions(self, accDBID):
        lastWeekThreshold = self._getTime() - SECONDS_PER_WEEK
        contributionRecord = self.playerContributions.get(accDBID, {})
        total = contributionRecord.get(TOTAL_CONTRIBUTION, 0)
        lastWeek = 0
        for stamp, value in contributionRecord.iteritems():
            if stamp != TOTAL_CONTRIBUTION and stamp >= lastWeekThreshold:
                lastWeek += value

        return (total, lastWeek)

    def _validateDefenceHour(self, timestamp, forbiddenDefenseHours = (), startingTimeOfNewDay = 0):
        timeNewDefHour, newDefHour, _ = self.events.get(FORT_EVENT_TYPE.DEFENCE_HOUR_CHANGE, (0, 0, 0))
        timeNewOffDay, newOffDay, _ = self.events.get(FORT_EVENT_TYPE.OFF_DAY_CHANGE, (0, 0, 0))
        return FortifiedRegionBase.validateDefenceHour(timestamp, self.defenceHour, self.offDay, self.vacationStart, self.vacationFinish, timeNewDefHour, newDefHour, timeNewOffDay, newOffDay, forbiddenDefenseHours, startingTimeOfNewDay)

    @staticmethod
    def validateDefenceHour(timestamp, defHour, offDay, timeVacationStart, timeVacationFinish, timeNewDefHour, newDefHour, timeNewOffDay, newOffDay, forbiddenDefenseHours = (), startingTimeOfNewDay = 0):
        if timeVacationStart <= timestamp <= timeVacationFinish:
            return FORT_ERROR.CLAN_ON_VACATION
        if timestamp % SECONDS_PER_HOUR != 0:
            return FORT_ERROR.NON_ALIGNED_TIMESTAMP
        dh = defHour if timeNewDefHour == 0 or timestamp < timeNewDefHour else newDefHour
        if dh < 0:
            return FORT_ERROR.DEF_HOUR_NOT_ACTIVE
        timeOfDay = timestamp % SECONDS_PER_DAY
        hourOfDay = timeOfDay / SECONDS_PER_HOUR
        if hourOfDay != dh:
            LOG_DEBUG_DEV('validateDefenceHour', hourOfDay, dh)
            return FORT_ERROR.BAD_HOUR_VALUE
        if hourOfDay in forbiddenDefenseHours:
            LOG_DEBUG_DEV('validateDefenceHour', hourOfDay, forbiddenDefenseHours)
            return FORT_ERROR.FORBIDDEN_FORT_BATTLE_HOUR
        od = offDay if timeNewOffDay == 0 or timestamp < timeNewOffDay else newOffDay
        if od >= 0:
            dayOfWeek = (timestamp - startingTimeOfNewDay) % SECONDS_PER_WEEK / SECONDS_PER_DAY
            dayOfWeek = (dayOfWeek + 3) % 7
            if od == dayOfWeek:
                return FORT_ERROR.CLAN_HAS_OFF_DAY
        return OK

    def _DEBUG_createFake(self):
        if self.dbID:
            return FORT_ERROR.ALREADY_CREATED
        self.dbID = 123
        self.state = 0
        self._devMode = IS_DEVELOPMENT
        self._debugTimeShift = 0
        self.influencePoints = 0
        self.creatorDBID = 1234
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
        self.level = 2
        self.dirMask = 3
        self.lockedDirMask = 0
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
        self.attacks = {}
        self.defences = {}
        self._lastAttacks = {}
        self.battles = {}
        self.battleUnits = {}
        self.sorties = {}
        self.consumables = {}
        self.consumablesMeta = {}
        self._sortieUnits = {}
        self.statistics = dossiers2.getFortifiedRegionsDossierDescr()
        self.favorites = set()
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
        buildingMapEventID = buildingTypeID + FORT_EVENT_TYPE.BUILDING_MAPS_BASE
        self.events.pop(buildingMapEventID, None)
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

    def _addInfluencePoints(self, influencePoints):
        LOG_OGNICK('_addInfluencePoints', influencePoints)
        self.storeOp(FORT_OP.ADD_INFLUENCE_POINTS, influencePoints)
        self.influencePoints += influencePoints

    def _createNew(self, clanDBID, creatorDBID, peripheryID, clanMemberDBIDs):
        LOG_DAN('Fort._createNew', clanDBID, creatorDBID, peripheryID, clanMemberDBIDs)
        self.dbID = clanDBID
        self.state = FORT_STATE.FORT_CREATED | FORT_STATE.PLANNED_INFO_LOADED
        self.peripheryID = peripheryID
        self.defenceHour = NOT_ACTIVATED
        self.offDay = NOT_ACTIVATED
        self.vacationStart = 0
        self.vacationFinish = 0
        self.events = {}
        self.level = 1
        self.dirMask = 0
        self.lockedDirMask = 0
        self._devMode = IS_DEVELOPMENT
        self._debugTimeShift = 0
        self.influencePoints = 0
        self.creatorDBID = creatorDBID
        self.buildings = {}
        building = BuildingDescr(typeID=FORT_BUILDING_TYPE.MILITARY_BASE, level=1)
        building.storage = fortified_regions.g_cache.startResource
        building.attachedPlayers = set(clanMemberDBIDs)
        self.buildings[FORT_BUILDING_TYPE.MILITARY_BASE] = building.makeCompactDescr()
        self._dirPosToBuildType = {0: [FORT_BUILDING_TYPE.MILITARY_BASE]}
        self._playerAttachments = dict.fromkeys(clanMemberDBIDs, FORT_BUILDING_TYPE.MILITARY_BASE)
        self.playerContributions = {}
        self.orders = {}
        self.attacks = {}
        self.defences = {}
        self._lastAttacks = {}
        self.battles = {}
        self.battleUnits = {}
        self.sorties = {}
        self._sortieUnits = {}
        self.consumables = {}
        self.consumablesMeta = {}
        self.statistics = dossiers2.getFortifiedRegionsDossierDescr()
        self.favorites = set()
        self.storeOp(FORT_OP.CREATE_NEW, clanDBID, creatorDBID, peripheryID, clanMemberDBIDs)

    SIZE_CREATE_NEW_HEADER = struct.calcsize('<qii')
    SIZE_DBID = struct.calcsize('<q')

    def _delete(self, deleterDBID):
        LOG_DAN('Fort._delete', deleterDBID, self.dbID)
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

    def _changeOrderCount(self, consumableTypeID, level, delta):
        LOG_OGNICK('Fort(id=%d)._changeOrderCount' % self.dbID, consumableTypeID, level, delta)
        count = self.orders.get(consumableTypeID, (0, 0))[0] + delta
        if not count >= 0:
            raise AssertionError
            self.orders[consumableTypeID] = count and (count, level)
        else:
            self.orders.pop(consumableTypeID, None)
        self.storeOp(FORT_OP.CHANGE_ORDER_COUNT, consumableTypeID, level, delta)
        return

    def _replaceConsumables(self, unitMgrID, peripheryID, timeExpire, prebattleType, oldRev, newRev, consumables):
        key = (unitMgrID, peripheryID)
        LOG_OGNICK('Fort(id=%d)._replaceConsumables oldRev=%d newRev=%d' % (self.dbID, oldRev, newRev), key, timeExpire, prebattleType, consumables)
        consumablesByRev = self.consumables.setdefault(key, {})
        consumablesByRev.pop(oldRev, None)
        if consumables:
            consumablesByRev[newRev] = consumables
        _, prebattleType, _, _ = self.consumablesMeta.get(key, (0,
         prebattleType,
         True,
         0))
        self.consumablesMeta[key] = (timeExpire,
         prebattleType,
         True,
         newRev)
        self.storeOp(FORT_OP.REPLACE_CONSUMABLES, unitMgrID, peripheryID, timeExpire, prebattleType, oldRev, newRev, consumables)
        return

    def _setUnitMgrIsDead(self, unitMgrID, peripheryID):
        key = (unitMgrID, peripheryID)
        LOG_OGNICK('Fort(id=%d)._setUnitMgrIsDead' % self.dbID, key)
        timeExpire, prebattleType, _, rev = self.consumablesMeta.get(key, (0,
         0,
         True,
         0))
        self.consumablesMeta[key] = (timeExpire,
         prebattleType,
         False,
         rev)
        self.storeOp(FORT_OP.SET_UNIT_MGR_IS_DEAD, unitMgrID, peripheryID)

    def _deleteConsumables(self, unitMgrID, peripheryID):
        key = (unitMgrID, peripheryID)
        LOG_OGNICK('Fort(id=%d)._deleteConsumables' % self.dbID, key)
        self.consumables.pop(key, None)
        self.consumablesMeta.pop(key, None)
        self.storeOp(FORT_OP.DELETE_CONSUMABLES, unitMgrID, peripheryID)
        return

    def _changeDefHour(self, newValue, timeActivation, timeCooldown, initiatorDBID):
        LOG_DEBUG_DEV('_changeDefHour', newValue, timeActivation, timeCooldown, initiatorDBID)
        self.events[FORT_EVENT_TYPE.DEFENCE_HOUR_CHANGE] = (timeActivation, newValue, initiatorDBID)
        self.events[FORT_EVENT_TYPE.DEFENCE_HOUR_COOLDOWN] = (timeCooldown, 0, 0)
        self.storeOp(FORT_OP.CHANGE_DEF_HOUR, newValue, timeActivation, timeCooldown, initiatorDBID)

    def _shutdownDefHour(self, timeActivation, initiatorDBID):
        LOG_DEBUG_DEV('_shutdownDefHour', timeActivation, initiatorDBID)
        self.events[FORT_EVENT_TYPE.DEFENCE_HOUR_SHUTDOWN] = (timeActivation, 0, initiatorDBID)
        self.storeOp(FORT_OP.SHUTDOWN_DEF_HOUR, timeActivation, initiatorDBID)

    def _changePeriphery(self, peripheryID, timeCooldown):
        LOG_DEBUG_DEV('_changePeriphery', peripheryID)
        self.events[FORT_EVENT_TYPE.PERIPHERY_COOLDOWN] = (timeCooldown, 0, 0)
        self.peripheryID = peripheryID
        self.storeOp(FORT_OP.CHANGE_PERIPHERY, peripheryID, timeCooldown)

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
        self.events[FORT_EVENT_TYPE.VACATION_FINISH] = (timeVacationEnd, 0, initiatorDBID)
        self.events[FORT_EVENT_TYPE.VACATION_COOLDOWN] = (timeCooldown, 0, 0)
        self.storeOp(FORT_OP.CHANGE_VACATION, timeVacationStart, timeVacationEnd, timeCooldown, initiatorDBID)

    def _expireEvent(self, eventTypeID, value):
        LOG_DEBUG_DEV('_expireEvent', eventTypeID, value)
        self.events.pop(eventTypeID, None)
        buildingTypeID = eventTypeID - FORT_EVENT_TYPE.PRODUCT_ORDERS_BASE
        if buildingTypeID in FORT_BUILDING_TYPE_NAMES:
            building = self.getBuilding(buildingTypeID)
            if not building.isProductionSuspended():
                building.orderInProduction.clear()
            self.setBuilding(buildingTypeID, building)
        elif eventTypeID == FORT_EVENT_TYPE.DEFENCE_HOUR_CHANGE:
            self._activateDefHour(value)
        elif eventTypeID == FORT_EVENT_TYPE.OFF_DAY_CHANGE:
            self.offDay = value
            self._broadcastFortSystemMessage(SYS_MESSAGE_FORT_EVENT.OFF_DAY_ACTIVATED, defenceHour=self.defenceHour, offDay=self.offDay)
        elif eventTypeID == FORT_EVENT_TYPE.VACATION_START:
            self._broadcastFortSystemMessage(SYS_MESSAGE_FORT_EVENT.VACATION_STARTED, timeStart=self.vacationStart, timeEnd=self.vacationFinish)
        elif eventTypeID == FORT_EVENT_TYPE.VACATION_FINISH:
            self._broadcastFortSystemMessage(SYS_MESSAGE_FORT_EVENT.VACATION_FINISHED)
        elif eventTypeID == FORT_EVENT_TYPE.DEFENCE_HOUR_SHUTDOWN:
            self.defenceHour = NOT_ACTIVATED
            self.validateBuildingMaps()
            self._shutdownDowngrade()
            self._broadcastFortSystemMessage(SYS_MESSAGE_FORT_EVENT.DEF_HOUR_SHUTDOWN)
        self.storeOp(FORT_OP.EXPIRE_EVENT, eventTypeID, value)
        return

    def _activateDefHour(self, value, initiatorDBID = 0):
        LOG_DEBUG_DEV('_activateDefHour', value, initiatorDBID)
        msgID = SYS_MESSAGE_FORT_EVENT.DEF_HOUR_ACTIVATED if self.defenceHour == NOT_ACTIVATED else SYS_MESSAGE_FORT_EVENT.DEF_HOUR_CHANGED
        self._broadcastFortSystemMessage(msgID, defenceHour=value)
        self.defenceHour = value
        self.validateBuildingMaps()

    def _shutdownDowngrade(self):
        if self.level > DEF_SHUTDOWN_LEVEL:
            LOG_DAN('_shutdownDowngrade', self.dbID, self.level, DEF_SHUTDOWN_LEVEL)
            self.level = DEF_SHUTDOWN_LEVEL
            for buildTypeID in self.buildings.keys():
                building = self.getBuilding(buildTypeID)
                if building.level > DEF_SHUTDOWN_LEVEL:
                    building.level = DEF_SHUTDOWN_LEVEL
                    building.levelRef = building.typeRef.levels.get(DEF_SHUTDOWN_LEVEL)
                    resCount = building.hp + building.storage
                    building.hp = min(resCount, building.levelRef.hp)
                    resCountLeft = resCount - building.hp
                    building.storage = min(resCountLeft, building.levelRef.storage)
                    resCountLost = resCountLeft - building.storage
                    self.setBuilding(buildTypeID, building)

            for orderTypeID in self.orders.keys():
                count, level = self.orders[orderTypeID]
                self.orders[orderTypeID] = (count, DEF_SHUTDOWN_LEVEL)

            for orderTypeID in (FORT_ORDER_TYPE.EVACUATION, FORT_ORDER_TYPE.REQUISITION):
                eventTypeID = FORT_EVENT_TYPE.ACTIVE_ORDERS_BASE + orderTypeID
                if eventTypeID in self.events:
                    _, value, _ = self.events[eventTypeID]
                    self._expireEvent(eventTypeID, value)

            for dir in xrange(1, MAX_DIRECTION_NUM + 1):
                lockedDirMask = self.lockedDirMask & ~(1 << dir)
                self._setLockedDirMask(lockedDirMask)

            self.offDay = NOT_ACTIVATED
            self.vacationStart = 0
            self.vacationFinish = 0
            for eventTypeID in self.events.keys():
                if eventTypeID in FORT_EVENT_TYPE._SHUTDOWN_EVENTS:
                    self.events.pop(eventTypeID)

            self._dirty = True

    def _addEvent(self, eventTypeID, timestamp, value, callerDBID):
        LOG_DEBUG_DEV('_addEvent', eventTypeID, timestamp, value, callerDBID)
        self.events[eventTypeID] = (timestamp, value, callerDBID)
        self.storeOp(FORT_OP.ADD_EVENT, eventTypeID, timestamp, value, callerDBID)

    def _cancelEvent(self, eventTypeID):
        LOG_DEBUG_DEV('_cancelEvent', eventTypeID)
        self.events.pop(eventTypeID, None)
        self.storeOp(FORT_OP.CANCEL_EVENT, eventTypeID)
        return

    def _setDevMode(self, isActive):
        LOG_DEBUG_DEV('_setDevMode', isActive)
        self._devMode = bool(isActive)
        self.storeOp(FORT_OP.SET_DEV_MODE, int(isActive))

    def _setTimeShift(self, timeShift):
        LOG_DEBUG_DEV('_setTimeShift', timeShift)
        self._debugTimeShift = timeShift
        self.storeOp(FORT_OP.SET_TIME_SHIFT, timeShift)

    def _openDir(self, dir, timestamp, initiatorDBID):
        LOG_DEBUG_DEV('_openDir', dir, timestamp, initiatorDBID)
        self.dirMask |= 1 << dir
        eventTypeID = FORT_EVENT_TYPE.DIR_OPEN_ATTACKS_BASE + dir
        self.events[eventTypeID] = (timestamp, 0, initiatorDBID)
        self.storeOp(FORT_OP.OPEN_DIR, dir, timestamp, initiatorDBID)

    def _closeDir(self, dir):
        LOG_DEBUG_DEV('_closeDir', dir)
        self.dirMask &= ~(1 << dir)
        eventTypeID = FORT_EVENT_TYPE.DIR_OPEN_ATTACKS_BASE + dir
        self.events.pop(eventTypeID, None)
        self.storeOp(FORT_OP.CLOSE_DIR, dir)
        return

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
            if level == 8:
                self._broadcastFortSystemMessage(SYS_MESSAGE_FORT_EVENT.FORT_GOT_8_LEVEL)
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

    def _addFortBattle(self, battleID, direction, attackTime, attackerClanDBID, defenderClanDBID, canUseEquipments, division):
        self.battles[battleID] = {'direction': direction,
         'isDefence': bool(defenderClanDBID == self.dbID),
         'attackTime': attackTime,
         'attackerClanDBID': attackerClanDBID,
         'defenderClanDBID': defenderClanDBID,
         'attackerBuildList': None,
         'defenderBuildList': None,
         'attackerFullBuildList': None,
         'defenderFullBuildList': None,
         'battleResultList': [],
         'prevBuildNum': 0,
         'currentBuildNum': 0,
         'isEnemyReadyForBattle': False,
         'roundStart': 0,
         'isBattleRound': 0,
         'canUseEquipments': canUseEquipments,
         'division': division}
        self.storeOp(FORT_OP.ADD_FORT_BATTLE, battleID, direction, attackTime, attackerClanDBID, defenderClanDBID, canUseEquipments, division)
        return

    def _removeFortBattle(self, battleID):
        self.battles.pop(battleID, None)
        self.battleUnits.pop(battleID, None)
        self.storeOp(FORT_OP.REMOVE_FORT_BATTLE, battleID)
        return

    def _setFortBattleBuildnum(self, battleID, packBuildsNum, roundStart = 0):
        battle = self.battles[battleID]
        prevBuildNum, currentBuildNum = parseDirPosByte(packBuildsNum)
        battle['prevBuildNum'] = prevBuildNum
        battle['currentBuildNum'] = currentBuildNum - 1
        battle['roundStart'] = roundStart
        self.storeOp(FORT_OP.SET_FORT_BATTLE_BUILDNUM, battleID, packBuildsNum, roundStart)

    def _setFortBattleResults(self, battleID, battleResult):
        battle = self.battles[battleID]
        battle['battleResultList'].append(battleResult)
        self.storeOp(FORT_OP.SET_FORT_BATTLE_RESULTS, battleID, battleResult)

    def _setFortBattleDirections(self, battleID, buildListStr):
        battle = self.battles[battleID]
        buildList = cPickle.loads(buildListStr)
        battle['attackerBuildList'] = buildList['attacker']
        battle['defenderBuildList'] = buildList['defender']
        battle['attackerFullBuildList'] = buildList['attackerFull']
        battle['defenderFullBuildList'] = buildList['defenderFull']
        self.storeOp(FORT_OP.SET_FORT_BATTLE_DIRECTIONS, battleID, buildListStr)

    def _setFortBattleRound(self, battleID, isBattleRound):
        battle = self.battles[battleID]
        battle['isBattleRound'] = int(isBattleRound)
        self.storeOp(FORT_OP.SET_FORT_BATTLE_ROUND, battleID, isBattleRound)

    def _setSortie(self, unitMgrID, cmdrDBID, rosterTypeID, state, peripheryID, count, maxCount, timestamp, igrType, cmdrName, strComment):
        LOG_DEBUG_DEV('_setSortie', unitMgrID, cmdrDBID, rosterTypeID, state, peripheryID, count, maxCount, timestamp, igrType, cmdrName, strComment)
        sortieKey = (unitMgrID, peripheryID)
        sortieArgs = (cmdrDBID,
         rosterTypeID,
         state,
         count,
         maxCount,
         timestamp,
         igrType,
         cmdrName,
         strComment)
        self.sorties[sortieKey] = sortieArgs
        self.storeOp(FORT_OP.ADD_SORTIE, unitMgrID, cmdrDBID, rosterTypeID, state, peripheryID, count, maxCount, timestamp, igrType, cmdrName, strComment)

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

    def _setEnemyReadyForBattle(self, battleID, isReady):
        LOG_DEBUG_DEV('_setEnemyReadyForBattle', battleID, isReady)
        battle = self.battles[battleID]
        battle['isEnemyReadyForBattle'] = isReady
        self.storeOp(FORT_OP.SET_ENEMY_READY_FOR_BATTLE, battleID, isReady)

    def _unpackFortBattleUnit(self, unpacking):
        battleID, = struct.unpack_from(self.FORMAT_FORT_BATTLE_UNIT_HEADER, unpacking)
        unit = UnitBase()
        unpacking = unit.unpack(unpacking[self.SIZE_FORT_BATTLE_UNIT_HEADER:])
        self.battleUnits[battleID] = unit.pack()
        return unpacking

    def _removeFortBattleUnit(self, battleID):
        self.battleUnits.pop(battleID, None)
        self.storeOp(FORT_OP.REMOVE_FORT_BATTLE_UNIT, battleID)
        return

    def _setState(self, newState):
        LOG_DEBUG_DEV('_setState', newState)
        self.state = newState
        self.storeOp(FORT_OP.SET_STATE, newState)

    def _processRequest(self, reqID, callerDBID):
        LOG_DEBUG_DEV('_processRequest', reqID, callerDBID)

    def _syncFortDossier(self, compDossierDescr):
        LOG_DEBUG_DEV('_syncFortDossier')
        self.statistics = dossiers2.getFortifiedRegionsDossierDescr(compDossierDescr)

    def _dmgBuilding(self, buildingTypeID, damage, attackerClanDBID):
        LOG_DEBUG_DEV('_dmgBuilding', buildingTypeID, damage, attackerClanDBID)
        building = self.getBuilding(buildingTypeID)
        building.setResource(building.hp + building.storage - damage)
        self.setBuilding(buildingTypeID, building)
        self.storeOp(FORT_OP.DMG_BUILDING, buildingTypeID, damage, attackerClanDBID)

    def _suspendProduction(self, buildingTypeID, timeLeft):
        LOG_DEBUG_DEV('_suspendProduction', buildingTypeID, timeLeft)
        building = self.getBuilding(buildingTypeID)
        building.orderInProduction.update(isSuspended=True, timeFinish=timeLeft)
        self.setBuilding(buildingTypeID, building)
        self.storeOp(FORT_OP.SUSPEND_PRODUCTION, buildingTypeID, timeLeft)

    def _resumeProduction(self, buildingTypeID, timeFinish):
        LOG_DEBUG_DEV('_resumeProduction', buildingTypeID, timeFinish)
        building = self.getBuilding(buildingTypeID)
        building.orderInProduction.update(isSuspended=False, timeFinish=timeFinish)
        self.setBuilding(buildingTypeID, building)
        level = building.level
        eventID = FORT_EVENT_TYPE.PRODUCT_ORDERS_BASE + buildingTypeID
        self.events[eventID] = (timeFinish, level, 0)
        self.storeOp(FORT_OP.RESUME_PRODUCTION, buildingTypeID, timeFinish)

    def _packClanCard(self, clan):
        timeNewDefHour, newDefHour, _ = self.events.get(FORT_EVENT_TYPE.DEFENCE_HOUR_CHANGE, (0, 0, 0))
        timeNewOffDay, newOffDay, _ = self.events.get(FORT_EVENT_TYPE.OFF_DAY_CHANGE, (0, 0, 0))
        dictBriefBuildings = {}
        for buildTypeID, buildCompDescr in self.buildings.iteritems():
            building = BuildingDescr(buildCompDescr)
            dirPosByte = makeDirPosByte(building.direction, building.position)
            dictBriefBuildings[buildTypeID] = {'level': building.level,
             'dirPosByte': dirPosByte,
             'hp': building.hp}

        now = int(time.time())
        listScheduledDefences = []
        for (attackTime, dirTo), args in self.defences.iteritems():
            if attackTime < now:
                continue
            clanDBID, clanAbbrev = args[:FORT_ATK_IDX.ENEMY_DIR]
            listScheduledDefences.append((attackTime,
             dirTo,
             clanDBID,
             clanAbbrev))

        dictDirOpenAttacks = {}
        for eventType, (timestamp, _, initiatorDBID) in self.events.iteritems():
            if eventType in xrange(FORT_EVENT_TYPE.DIR_OPEN_ATTACKS_FIRST, FORT_EVENT_TYPE.DIR_OPEN_ATTACKS_LAST + 1):
                dir = eventType - FORT_EVENT_TYPE.DIR_OPEN_ATTACKS_BASE
                dictDirOpenAttacks[dir] = timestamp

        LOG_DEBUG_DEV('_packClanCard', dictBriefBuildings, listScheduledDefences, dictDirOpenAttacks)
        return self._getOpPack(FORT_OP.ENEMY_CLAN_CARD, self.dbID, self.level, self.dirMask, self.defenceHour, self.offDay, self.vacationStart, self.vacationFinish, timeNewDefHour, timeNewOffDay, newDefHour, newOffDay, clan.name, clan.abbreviation, clan.description, clan.motto, self.statistics.makeCompDescr(), dictBriefBuildings, listScheduledDefences, dictDirOpenAttacks)

    def _onEnemyClanCard(self, clanDBID, fortLevel, dirMask, defHour, offDay, vacationStart, vacationFinish, timeNewDefHour, timeNewOffDay, newDefHour, newOffDay, clanName, clanAbbrev, clanDescr, clanMotto, statistics, dictBuildingsBrief, listScheduledAttacks, dictDirOpenAttacks):
        pass

    def _onDeleteBattle(self, key, args, reason, isDefence):
        battleID = args[FORT_ATK_IDX.BATTLE_ID]
        self.battles.pop(battleID, None)
        return

    def _deleteBattleByID(self, battleID, reason):
        LOG_DEBUG_DEV('_deleteBattleByID', battleID, reason, self.dbID)
        self.battles.pop(battleID, None)
        self.storeOp(FORT_OP.DELETE_BATTLE_BY_ID, battleID, reason)
        return

    def _deleteBattlesByTime(self, timeStart, timeFinish, dir, reason):
        LOG_DEBUG_DEV('_deleteBattlesByTime', timeStart, timeFinish, dir, reason, self.dbID)
        for key in self.attacks.keys():
            timeAttack, dirFrom = key
            if dir != ALL_DIRS and dir != dirFrom:
                continue
            if timeStart <= timeAttack and timeAttack <= timeFinish:
                args = self.attacks.pop(key)
                self._onDeleteBattle(key, args, reason, isDefence=False)

        for key in self.defences.keys():
            timeAttack, dirTo = key
            if dir != ALL_DIRS and dir != dirTo:
                continue
            if timeStart <= timeAttack and timeAttack <= timeFinish:
                args = self.defences.pop(key)
                self._onDeleteBattle(key, args, reason, isDefence=True)

        self._rebuildLastAttackIndexes()
        self.storeOp(FORT_OP.DELETE_BATTLES_BY_TIME, timeStart, timeFinish, dir, reason)

    def _deleteBattlesByClan(self, enemyClanDBID, timeStart, timeFinish, enemyDir, reason):
        LOG_DEBUG_DEV('_deleteBattlesByClan', enemyClanDBID, timeStart, timeFinish, enemyDir, reason, self.dbID)
        for key in self.attacks.keys():
            timeAttack, dirFrom = key
            defenderClanDBID = self.attacks[key][FORT_ATK_IDX.ENEMY_DBID]
            dirTo = self.attacks[key][FORT_ATK_IDX.ENEMY_DIR]
            if enemyDir != ALL_DIRS and enemyDir != dirTo:
                continue
            if defenderClanDBID == enemyClanDBID and timeStart <= timeAttack <= timeFinish:
                args = self.attacks.pop(key)
                self._onDeleteBattle(key, args, reason, isDefence=True)

        for key in self.defences.keys():
            timeAttack, dirTo = key
            attackerClanDBID = self.defences[key][FORT_ATK_IDX.ENEMY_DBID]
            dirFrom = self.defences[key][FORT_ATK_IDX.ENEMY_DIR]
            if enemyDir != ALL_DIRS and enemyDir != dirFrom:
                continue
            if attackerClanDBID == enemyClanDBID and timeStart <= timeAttack <= timeFinish:
                args = self.defences.pop(key)
                self._onDeleteBattle(key, args, reason, isDefence=True)

        self._rebuildLastAttackIndexes()
        self.storeOp(FORT_OP.DELETE_BATTLES_BY_CLAN, enemyClanDBID, timeStart, timeFinish, enemyDir, reason)

    def _addAttack(self, timeAttack, dirFrom, dirTo, defClanDBID, battleID, attackerFortLevel, defenderFortLevel, division, peripheryID, attackResult, attackResource, defClanAbbrev):
        LOG_DEBUG_DEV('_addAttack', timeAttack, dirFrom, dirTo, defClanDBID, battleID, attackerFortLevel, defenderFortLevel, division, peripheryID, attackResult, attackResource, defClanAbbrev, self.dbID)
        self.attacks[timeAttack, dirFrom] = (defClanDBID,
         defClanAbbrev,
         dirTo,
         battleID,
         attackerFortLevel,
         defenderFortLevel,
         division,
         peripheryID,
         attackResult,
         attackResource)
        lastTime = self._lastAttacks.get(defClanDBID, 0)
        if timeAttack > lastTime:
            self._lastAttacks[defClanDBID] = timeAttack
        self.storeOp(FORT_OP.ADD_ATTACK, timeAttack, dirFrom, dirTo, defClanDBID, battleID, attackerFortLevel, defenderFortLevel, division, peripheryID, attackResult, attackResource, defClanAbbrev)

    def _addDefence(self, timeAttack, dirFrom, dirTo, attackerClanDBID, battleID, attackerFortLevel, defenderFortLevel, division, attackResult, attackResource, attackerClanAbbrev):
        LOG_DEBUG_DEV('_addDefence', timeAttack, dirFrom, dirTo, attackerClanDBID, battleID, attackerFortLevel, defenderFortLevel, division, attackResult, attackResource, attackerClanAbbrev, self.dbID)
        self.defences[timeAttack, dirTo] = (attackerClanDBID,
         attackerClanAbbrev,
         dirFrom,
         battleID,
         attackerFortLevel,
         defenderFortLevel,
         division,
         attackResult,
         attackResource)
        self.storeOp(FORT_OP.ADD_DEFENCE, timeAttack, dirFrom, dirTo, attackerClanDBID, battleID, attackerFortLevel, defenderFortLevel, division, attackResult, attackResource, attackerClanAbbrev)

    def _setLockedDirMask(self, lockedDirMask):
        LOG_DEBUG_DEV('_setLockedDirMask', lockedDirMask)
        self.lockedDirMask = lockedDirMask
        self.storeOp(FORT_OP.SET_LOCKED_DIRS, lockedDirMask)

    def _setAttackResult(self, attackResult, attackResource, attackerClanDBID, attackerDirection, attackTime):
        LOG_DEBUG_DEV('_setAttackResult', attackResult, attackResource, attackerClanDBID, attackerDirection, attackTime, self.dbID)
        if attackerClanDBID == self.dbID:
            key = (attackTime, attackerDirection)
            if key in self.attacks:
                clanDBID, clanAbbrev, dirTo, battleID, atkLevel, defLevel, division, peripheryID, _, _ = self.attacks[key]
                self.attacks[key] = (clanDBID,
                 clanAbbrev,
                 dirTo,
                 battleID,
                 atkLevel,
                 defLevel,
                 division,
                 peripheryID,
                 attackResult,
                 attackResource)
        else:
            for key in self.defences.keys():
                defenceTime, defenceDir = key
                if defenceTime != attackTime:
                    continue
                clanDBID, clanAbbrev, dirFrom, battleID, atkLevel, defLevel, division, _, _ = self.defences[key]
                if attackerClanDBID == clanDBID and attackerDirection == dirFrom:
                    self.defences[key] = (clanDBID,
                     clanAbbrev,
                     dirFrom,
                     battleID,
                     atkLevel,
                     defLevel,
                     division,
                     attackResult,
                     attackResource)
                    break

        self.storeOp(FORT_OP.SET_ATTACK_RESULT, attackResult, attackResource, attackerClanDBID, attackerDirection, attackTime)

    def _addFavorite(self, clanDBID):
        LOG_DEBUG_DEV('_addFavorite', clanDBID)
        self.favorites.add(clanDBID)
        self.storeOp(FORT_OP.ADD_FAVORITE, clanDBID)

    def _removeFavorite(self, clanDBID):
        LOG_DEBUG_DEV('_removeFavorite', clanDBID)
        self.favorites.discard(clanDBID)
        self.storeOp(FORT_OP.REMOVE_FAVORITE, clanDBID)

    def _onEmergencyRestore(self, unpacking):
        LOG_DEBUG_DEV('_onEmergencyRestore')
        return unpacking

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

    def _setPeriphery(self, peripheryID):
        self.peripheryID = peripheryID
        self.storeOp(FORT_OP.SET_PERIPHERY, peripheryID)

    def _setInfluencePoints(self, influencePoints):
        LOG_OGNICK('_setInfluencePoints', influencePoints)
        self.influencePoints = influencePoints
        self.storeOp(FORT_OP.SET_INFLUENCE_POINTS, influencePoints)
