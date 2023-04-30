# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/UnitBase.py
import cPickle
import copy
import struct
import weakref
from collections import namedtuple
from typing import TYPE_CHECKING
from constants import VEHICLE_CLASS_INDICES, PREBATTLE_TYPE, QUEUE_TYPE, INVITATION_TYPE, BATTLE_MODE_VEHICLE_TAGS
from debug_utils import LOG_DEBUG, LOG_DEBUG_DEV
from items import vehicles
from items.badges_common import BadgesCommon
from UnitRoster import BaseUnitRosterSlot, _BAD_CLASS_INDEX, buildNamesDict, reprBitMaskFromDict
from ops_pack import OpsUnpacker, packPascalString, unpackPascalString, initOpsFormatDef
from unit_helpers.ExtrasHandler import EmptyExtrasHandler, ClanBattleExtrasHandler
from unit_helpers.ExtrasHandler import SquadExtrasHandler, ExternalExtrasHandler
from unit_roster_config import SquadRoster, UnitRoster, SpecRoster, EventRoster, EpicRoster, BattleRoyaleRoster, MapBoxRoster, FunRandomRoster, Comp7Roster
if TYPE_CHECKING:
    from typing import List as TList, Tuple as TTuple, Dict as TDict
UnitVehicle = namedtuple('UnitVehicle', ('vehInvID', 'vehTypeCompDescr', 'vehLevel', 'vehClassIdx'))
ProfileVehicle = namedtuple('ProfileVehicle', ('vehCompDescr', 'vehOutfitCD', 'seasonType', 'marksOnGun'))

class UNIT_MGR_STATE:
    IDLE = 0
    IN_QUEUE = 1
    IN_PRE_ARENA = 2
    IN_AUTO_SEARCH = 3
    REQUEUE_ASSEMBLER = 4
    FINISH_ASSEMBLING_ACCOUNTS = 5


class UNIT_FLAGS:
    LOCKED = 1
    INVITE_ONLY = 2
    IN_QUEUE = 4
    IN_SEARCH = 8
    DEV_MODE = 16
    IN_ARENA = 32
    SORTIES_FORBIDDEN = 64
    RATED_BATTLE_FORBIDDEN = 128
    IN_PRE_ARENA = 256
    IS_EXTERNAL_LOCK = 512
    IS_DYNAMIC = 1024
    ARENA_FINISHED = 2048
    KEEP_OFFLINE_ROSTER = 4096
    EXTERNAL_LEGIONARIES_MATCHING = 8192
    FINISH_ASSEMBLING = 16384
    DEFAULT = 0
    PRE_QUEUE = 0
    PRE_SEARCH = 0
    IN_ROSTER_WAIT = 0
    MODAL_STATES = IN_QUEUE | IN_ARENA
    CHANGED_STATE_ASQ = IN_ARENA | IN_PRE_ARENA | IN_SEARCH | IN_QUEUE


UNIT_STATE_NAMES = buildNamesDict(UNIT_FLAGS)

class UNIT_BROWSER_TYPE:
    NOT_RATED_UNITS = 1
    ALL = NOT_RATED_UNITS


UNIT_BROWSER_TYPE_NAMES = buildNamesDict(UNIT_BROWSER_TYPE)

class UNIT_CREATE_TYPE:
    DEFAULT = 0
    FALLOUT = 1
    SQUAD = 2
    EVENT = 3
    EXPOSED_TYPES = (DEFAULT,
     FALLOUT,
     SQUAD,
     EVENT)


class UNIT_ERROR:
    OK = 0
    ALREADY_JOINED_UNIT = 1
    UNIT_MGR_ENTITY_CREATION_FAIL = 2
    UNIT_ADD_FAIL = 3
    CANT_FIND_UNIT_MGR = 4
    ADD_PLAYER_FAIL = 5
    NO_UNIT_MGR = 6
    WRONG_UNIT_REQUISITES = 7
    REMOVE_PLAYER_FAIL = 8
    GET_VEHICLE_FAIL = 9
    ADD_MEMBER_FAIL = 10
    SET_MEMBER_READY_FAIL = 11
    ASSIGN_MEMBER_FAIL = 12
    FAIL_UNIT_METHOD = 13
    BAD_SLOT_IDX = 14
    INSUFFICIENT_ROLE = 15
    NO_UNIT = 16
    BAD_ROSTER_PACK = 17
    TOO_MANY_ROSTERS = 18
    JOIN_CTX_LOCK = 19
    CANT_INVITE = 20
    TIMEOUT = 21
    NOT_READY = 22
    NOT_IN_QUEUE = 23
    NOT_IDLE = 24
    NOT_IN_SEARCH = 25
    BAD_JOINING_ACC = 26
    PLAYER_IGNORED = 27
    NOT_INVITED = 28
    REMOVED_PLAYER = 29
    OFFLINE_PLAYER = 30
    KICKED_PLAYER = 31
    UNIT_RESTORED = 32
    ACCOUNT_RESTORED = 33
    GET_READY_VEHICLE_FAIL = 34
    COOLDOWN = 35
    ALREADY_INVITED = 37
    HAS_IN_ARENA_MEMBERS = 38
    KICKED_CANDIDATE = 39
    INVITE_REMOVED = 40
    BAD_ACCOUNT_TYPE = 41
    BAD_POINTS_SUM = 42
    WAITING_FOR_JOIN = 43
    BAD_VEHICLE_LEVEL = 44
    CLAN_CHANGED = 45
    NO_CLAN_MEMBERS = 46
    BAD_CLAN = 47
    NO_PLAYER = 48
    SLOT_RESERVED = 49
    SLOT_OCCUPIED = 50
    TOO_MANY_CLOSED_SLOTS = 51
    SLOT_NOT_CLOSED = 52
    CANT_PICK_LEADER = 53
    RESTRICT_LEGIONARIES = 54
    RESTRICT_INVITED = 55
    VEHICLE_MISMATCH = 56
    NO_VEHICLES = 57
    TOO_MANY_LEGIONARIES = 58
    VEHICLE_NOT_CHOSEN = 59
    ALREADY_IN_SLOT = 60
    FORT_BATTLE_END = 61
    NO_AVAILABLE_SLOTS = 62
    TOO_FEW_POINTS = 63
    BAD_DIVISION = 64
    CANT_CHANGE_DIVISION = 65
    CANNOT_LEAD = 66
    WRONG_UNITMGR = 68
    LEGIONARIES_FORBIDDEN = 69
    PREV_RATED_BATTLE_IN_PROGRESS = 70
    OFF_SEASON = 71
    BAD_PARAMS = 72
    PLAYER_READY = 73
    SORTIES_FORBIDDEN = 74
    NO_UNIT_ASSEMBLER = 75
    SPEC_BATTLE_END = 77
    BAD_VEHICLE_TYPE = 78
    TOO_FEW_VEHICLE_TYPE = 79
    TOO_MANY_VEHICLE_TYPE = 80
    TOO_FEW_VEHICLES = 81
    TOO_MANY_VEHICLES = 82
    BAD_FALLOUT_TYPE = 83
    BAD_VEHICLES_SET = 84
    WRONG_UNIT_API = 85
    NO_ACCOUNT = 86
    ASYNC_CALL_FAILED = 87
    BAD_WGSH_CMD = 88
    FAIL_EXT_BATTLE_MGR_CALL = 89
    FAIL_EXT_ACCOUNT_CALL = 90
    FAIL_EXT_UNIT_MGR_CALL = 91
    FAIL_EXT_UNIT_QUEUE_CALL = 92
    UNIT_DESTROYED = 93
    UNIT_NOT_IN_QUEUE = 94
    UNIT_LOCKED_IN_QUEUE = 95
    UNIT_KICKED_FROM_QUEUE = 96
    UNIT_BACK_TO_QUEUE = 97
    EXTERNAL_UNIT_NOT_ENABLED = 98
    BAD_ARENA_BONUS_TYPE = 99
    UNIT_CHANGED_LEADER = 100
    FAIL_EXT_UNIT_QUEUE_START = 101
    WRONG_VEHICLE = 102
    KICKED_PLAYER_TO_JOIN_ASSEMBLED_UNIT = 103
    UNIT_ASSEMBLER_NO_MATCH_POSSIBLE = 104
    UNIT_ASSEMBLER_UNIT_NOT_SUPPORTED = 105
    UNIT_ASSEMBLER_NO_DATE_RECEIVED = 106
    UNIT_ASSEMBLER_DISABLED = 107
    UNIT_ASSEMBLER_TIMEOUT = 108
    KICKED_SEARCH_ONLY_PLAYER = 109
    INVALID_ACCOUNT = 110
    ACCOUNT_BANNED = 111
    MODE_OFFLINE = 112
    NO_ARENA_VEHICLES = 113
    EXPIRED_PLAY_LIMITS = 114
    EXPIRED_PLAY_LIMITS_TO_COMMANDER = 115


OK = UNIT_ERROR.OK
UNIT_ERROR_NAMES = dict(((v, k) for k, v in UNIT_ERROR.__dict__.iteritems()))

class UNIT_SLOT:
    ANY = -1
    REMOVE = -2


INV_ID_CLEAR_VEHICLE = 0
LEADER_SLOT = 0
UNIT_CONFIRMATION_WAIT_TIME = 5.0
MAX_UNIT_ROSTER_ELEMENTS = 14
UNDEFINED_ESTIMATED_TIME = -1
INFINITY_ESTIMATED_TIME = 0

class UNIT_OP:
    SET_VEHICLE = 1
    SET_MEMBER = 2
    DEL_MEMBER = 3
    ADD_PLAYER = 4
    REMOVE_PLAYER = 5
    READY_MASK = 6
    SET_SLOT = 7
    CLEAR_VEHICLE = 8
    VEHICLE_DICT = 9
    UNIT_FLAGS = 10
    CLOSE_SLOT = 11
    OPEN_SLOT = 12
    SET_COMMENT = 13
    CHANGE_ROLE = 14
    MODAL_TIMESTAMP = 15
    GIVE_LEADERSHIP = 16
    EXTRAS_UPDATE = 18
    EXTRAS_RESET = 19
    GAMEPLAYS_MASK = 20
    SET_VEHICLE_LIST = 21
    ARENA_TYPE = 23
    SET_PLAYER_PROFILE = 24
    DEL_PLAYER_PROFILE = 25
    ESTIMATED_TIME_IN_QUEUE = 26
    ONLY_10_MODE = 27
    CLEAR_SEARCH_FLAGS = 28
    REMOVE_SEARCH_FLAGS = 29
    SET_SEARCH_FLAGS = 30
    SQUAD_SIZE = 31


class UNIT_ROLE:
    DEFAULT = 0
    INVITED = 1
    COMMANDER_UPDATES = 2
    CHANGE_ROSTER = 4
    LEGIONARY = 16
    MANAGER = 32
    IN_ARENA = 64
    OFFLINE = 128
    CAN_LEAD = 256
    AUTO_SEARCH = 512
    CAN_USE_EXTRA_EQUIPMENTS = 1024
    CAN_USE_BOOST_EQUIPMENTS = 2048
    START_STOP_BATTLE = CHANGE_ROSTER
    ADD_REMOVE_MEMBERS = CHANGE_ROSTER
    INVITE_KICK_PLAYERS = CHANGE_ROSTER
    CREATOR = COMMANDER_UPDATES | CHANGE_ROSTER
    CHANGE_LEADERSHIP = CREATOR | MANAGER
    SOCIAL_ROLES = LEGIONARY | MANAGER | CAN_LEAD
    SELF_ONLY = 65536
    SELF_UNLOCKED = 131072
    NON_IDLE = 262144
    NO_LEGIONARY_CANDIDATES = 524288
    PRE_ARENA = 1048576
    IN_AUTO_SEARCH = 2097152


UNIT_ROLE_NAMES = buildNamesDict(UNIT_ROLE)
VEHICLE_CLASS_SPG = VEHICLE_CLASS_INDICES.get('SPG', _BAD_CLASS_INDEX)

class UNIT_BROWSER_CMD:
    REFRESH = 0
    LEFT = 1
    RIGHT = 2


class UNIT_BROWSER_ERROR:
    OK = 0
    UNSUBSCRIBED = 1
    PAGING_ERROR = 2
    ACCEPT_TIMEOUT = 3
    BAD_ACCEPT_CONTEXT = 4
    SEARCH_CANCELED = 5
    ACCEPT_CANCELED = 6
    ALREADY_SUBSCRIBED = 7
    NOT_SUBSCRIBED = 8
    SERVICE_UNAVAILABLE = 9
    BAD_ACCOUNT_TYPE = 10
    COOLDOWN = 11


class UNIT_PUBLISHER_ERROR:
    OK = 0
    ALREADY_PUBLISHED = 1
    NOT_PUBLISHED = 2


class UNIT_NOTIFY_CMD:
    SET_VEHICLE_LIST = 1
    PLAYER_ONLINE = 2
    TRANSFER_LEADERSHIP = 3
    PUBLISH_STATE_CHANGE = 4
    SET_MEMBER_READY = 5
    KICK_ALL = 6
    EXTRAS_UPDATED = 7
    AUTO_ASSEMBLED_MEMBER_ADDED = 11
    APPROVED_VEHICLE_LIST = 12
    REMOVED_VEHICLE = 13
    UPD_VEHICLE_DESCRS = 14
    REMOVED_VEHICLE_MAX_SPG_EXCEED = 15
    REMOVED_VEHICLE_FROM_FILTER = 16
    INCORRECT_EVENT_ENQUEUE_DATA = 17
    REMOVED_VEHICLE_MAX_SCOUT_EXCEED = 18
    CHANGE_SQUAD_SIZE = 19
    PLAYER_LIMITS_EXPIRED = 20


class CLIENT_UNIT_CMD:
    NONE = 0
    LEAVE_UNIT = 1
    START_UNIT_BATTLE = 2
    STOP_UNIT_BATTLE = 3
    START_AUTO_SEARCH = 4
    STOP_AUTO_SEARCH = 5
    SET_UNIT_MEMBER = 6
    SET_UNIT_VEHICLE = 7
    FIT_UNIT_MEMBER = 8
    ASSIGN_UNIT_MEMBER = 9
    REASSIGN_UNIT_MEMBER = 10
    SET_UNIT_MEMBER_READY = 11
    KICK_UNIT_PLAYER = 12
    LOCK_UNIT = 13
    OPEN_UNIT = 14
    CLOSE_UNIT_SLOT = 15
    SET_ROSTER_SLOT = 16
    SET_UNIT_COMMENT = 17
    SET_UNIT_DEV_MODE = 18
    GIVE_LEADERSHIP = 19
    SET_GAMEPLAYS_MASK = 22
    SET_VEHICLE_LIST = 23
    SET_UNIT_VEHICLE_TYPE = 25
    SET_ARENA_TYPE = 26
    SET_ONLY_10_MODE = 27
    SET_SQUAD_SIZE = 28
    CHANGE_FUN_EVENT_ID = 29


CMD_NAMES = dict([ (v, k) for k, v in CLIENT_UNIT_CMD.__dict__.items() if not k.startswith('__') ])
FORCED_CLIENT_UNIT_CMDS = (CLIENT_UNIT_CMD.LEAVE_UNIT,)

class UNIT_NOTIFY_ID:
    PARENT_UNIT_MGR = -1


class UNIT_MGR_FLAGS:
    DEFAULT = 0
    SQUAD = 64
    SPEC_BATTLE = 128
    FALLOUT_CLASSIC = 256
    FALLOUT_MULTITEAM = 512
    EVENT = 1024
    STRONGHOLD = 2048
    EPIC = 4096
    TOURNAMENT = 8192
    BATTLE_ROYALE = 16384
    MAPBOX = 32768
    RTS = 65536
    FUN_RANDOM = 131072
    COMP7 = 262144


class UnitAssemblerSearchFlags(object):
    NO_FILTER = 0
    USE_VOICE = 1
    VEH_TIER_1 = 2
    VEH_TIER_2 = 4
    VEH_TIER_3 = 8
    VEH_TIER_4 = 16
    VEH_TIER_5 = 32
    VEH_TIER_6 = 64
    VEH_TIER_7 = 128
    VEH_TIER_8 = 256
    VEH_TIER_9 = 512
    VEH_TIER_10 = 1024
    DESTROY_UNIT_ON_ABORT = 2048
    ALL_VEH_TIERS = VEH_TIER_1 | VEH_TIER_2 | VEH_TIER_3 | VEH_TIER_4 | VEH_TIER_5 | VEH_TIER_6 | VEH_TIER_7 | VEH_TIER_8 | VEH_TIER_9 | VEH_TIER_10


class UnitAssemblerImplType(object):
    SQUAD = 1
    EPIC = 2


UNIT_ASSEMBLER_IMPL_TO_CONFIG = {UnitAssemblerImplType.SQUAD: 'squad',
 UnitAssemblerImplType.EPIC: 'epic'}
PREBATTLE_TYPE_TO_UNIT_ASSEMBLER = {PREBATTLE_TYPE.SQUAD: UnitAssemblerImplType.SQUAD,
 PREBATTLE_TYPE.EPIC: UnitAssemblerImplType.EPIC}

class BitfieldHelper:

    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @staticmethod
    def bitToFlag(bit):
        return 1 << bit

    def setFlag(self, flag):
        self._value |= flag

    def setBit(self, bit):
        self.setFlag(self.bitToFlag(bit))

    def unsetFlag(self, flag):
        if self.isSetFlag(flag):
            self.toggleFlag(flag)

    def unsetBit(self, bit):
        if self.isSetBit(bit):
            self.toggleBit(bit)

    def isSetFlag(self, flag):
        return self._value & flag == flag

    def isSetBit(self, bit):
        return self.isSetFlag(self.bitToFlag(bit))

    def toggleFlag(self, flag):
        self._value ^= flag

    def toggleBit(self, bit):
        self.toggleFlag(self.bitToFlag(bit))

    def compare(self, value):
        return self.value & value


VEHICLE_TAGS_GROUP_BY_UNIT_MGR_FLAGS = {UNIT_MGR_FLAGS.EVENT: (('event_battles',), tuple()),
 UNIT_MGR_FLAGS.EPIC: (tuple(), BATTLE_MODE_VEHICLE_TAGS - {'epic_battles'}),
 UNIT_MGR_FLAGS.BATTLE_ROYALE: (('battle_royale',), tuple()),
 UNIT_MGR_FLAGS.STRONGHOLD: (tuple(), BATTLE_MODE_VEHICLE_TAGS - {'clanWarsBattles'}),
 UNIT_MGR_FLAGS.COMP7: (tuple(), BATTLE_MODE_VEHICLE_TAGS - {'comp7'})}
UNIT_MGR_FLAGS_TO_PREBATTLE_TYPE = {UNIT_MGR_FLAGS.EVENT: PREBATTLE_TYPE.EVENT,
 UNIT_MGR_FLAGS.EPIC: PREBATTLE_TYPE.EPIC,
 UNIT_MGR_FLAGS.BATTLE_ROYALE: PREBATTLE_TYPE.BATTLE_ROYALE,
 UNIT_MGR_FLAGS.MAPBOX: PREBATTLE_TYPE.MAPBOX,
 UNIT_MGR_FLAGS.SQUAD: PREBATTLE_TYPE.SQUAD,
 UNIT_MGR_FLAGS.SPEC_BATTLE: PREBATTLE_TYPE.CLAN,
 UNIT_MGR_FLAGS.STRONGHOLD: PREBATTLE_TYPE.STRONGHOLD,
 UNIT_MGR_FLAGS.TOURNAMENT: PREBATTLE_TYPE.TOURNAMENT,
 UNIT_MGR_FLAGS.COMP7: PREBATTLE_TYPE.COMP7}

def _prebattleTypeFromFlags(flags):
    flag = flags ^ UNIT_MGR_FLAGS.SQUAD if flags != UNIT_MGR_FLAGS.SQUAD and flags & UNIT_MGR_FLAGS.SQUAD else flags
    for unitMgrFlag, prbType in UNIT_MGR_FLAGS_TO_PREBATTLE_TYPE.iteritems():
        if flag & unitMgrFlag:
            return prbType

    return PREBATTLE_TYPE.UNIT


UNIT_MGR_FLAGS_TO_UNIT_MGR_ENTITY_NAME = {UNIT_MGR_FLAGS.EVENT: 'EventUnitMgr',
 UNIT_MGR_FLAGS.MAPBOX: 'MapBoxUnitMgr',
 UNIT_MGR_FLAGS.SQUAD: 'SquadUnitMgr',
 UNIT_MGR_FLAGS.EPIC: 'SquadUnitMgr',
 UNIT_MGR_FLAGS.BATTLE_ROYALE: 'SquadUnitMgr',
 UNIT_MGR_FLAGS.SPEC_BATTLE: 'SpecUnitMgr',
 UNIT_MGR_FLAGS.STRONGHOLD: 'StrongholdUnitMgr',
 UNIT_MGR_FLAGS.COMP7: 'Comp7UnitMgr'}

def _entityNameFromFlags(flags):
    flag = flags ^ UNIT_MGR_FLAGS.SQUAD if flags != UNIT_MGR_FLAGS.SQUAD and flags & UNIT_MGR_FLAGS.SQUAD else flags
    for unitMgrFlag, unitMgrName in UNIT_MGR_FLAGS_TO_UNIT_MGR_ENTITY_NAME.iteritems():
        if flag & unitMgrFlag:
            return unitMgrName


UNIT_MGR_FLAGS_TO_INVITATION_TYPE = {UNIT_MGR_FLAGS.EVENT: INVITATION_TYPE.EVENT,
 UNIT_MGR_FLAGS.EPIC: INVITATION_TYPE.EPIC,
 UNIT_MGR_FLAGS.BATTLE_ROYALE: INVITATION_TYPE.BATTLE_ROYALE,
 UNIT_MGR_FLAGS.MAPBOX: INVITATION_TYPE.MAPBOX,
 UNIT_MGR_FLAGS.SQUAD: INVITATION_TYPE.SQUAD,
 UNIT_MGR_FLAGS.DEFAULT: INVITATION_TYPE.SQUAD,
 UNIT_MGR_FLAGS.COMP7: INVITATION_TYPE.COMP7}

def _invitationTypeFromFlags(flags):
    flag = flags ^ UNIT_MGR_FLAGS.SQUAD if flags != UNIT_MGR_FLAGS.SQUAD and flags & UNIT_MGR_FLAGS.SQUAD else flags
    for unitMgrFlag, invitationType in UNIT_MGR_FLAGS_TO_INVITATION_TYPE.iteritems():
        if flag & unitMgrFlag:
            return invitationType

    return None


def _unitAssemblerTypeFromFlags(flags):
    return PREBATTLE_TYPE_TO_UNIT_ASSEMBLER.get(_prebattleTypeFromFlags(flags), None)


UNIT_MGR_FLAGS_TO_QUEUE_TYPE = {UNIT_MGR_FLAGS.EVENT: QUEUE_TYPE.EVENT_BATTLES,
 UNIT_MGR_FLAGS.EPIC: QUEUE_TYPE.EPIC,
 UNIT_MGR_FLAGS.BATTLE_ROYALE: QUEUE_TYPE.BATTLE_ROYALE,
 UNIT_MGR_FLAGS.MAPBOX: QUEUE_TYPE.MAPBOX,
 UNIT_MGR_FLAGS.SQUAD: QUEUE_TYPE.RANDOMS,
 UNIT_MGR_FLAGS.COMP7: QUEUE_TYPE.COMP7}

def _queueTypeFromFlags(flags):
    flag = flags ^ UNIT_MGR_FLAGS.SQUAD if flags != UNIT_MGR_FLAGS.SQUAD and flags & UNIT_MGR_FLAGS.SQUAD else flags
    for unitMgrFlag, queueType in UNIT_MGR_FLAGS_TO_QUEUE_TYPE.iteritems():
        if flag & unitMgrFlag:
            return queueType

    return None


def extendTiersFilter(filterFlags):
    return (filterFlags << 1 | filterFlags | filterFlags >> 1) & UnitAssemblerSearchFlags.ALL_VEH_TIERS


class ROSTER_TYPE:
    UNIT_ROSTER = 0
    FALLOUT_CLASSIC_ROSTER = UNIT_MGR_FLAGS.SQUAD | UNIT_MGR_FLAGS.FALLOUT_CLASSIC
    FALLOUT_MULTITEAM_ROSTER = UNIT_MGR_FLAGS.SQUAD | UNIT_MGR_FLAGS.FALLOUT_MULTITEAM
    SQUAD_ROSTER = UNIT_MGR_FLAGS.SQUAD
    SPEC_ROSTER = UNIT_MGR_FLAGS.SPEC_BATTLE
    EVENT_ROSTER = UNIT_MGR_FLAGS.SQUAD | UNIT_MGR_FLAGS.EVENT
    STRONGHOLD_ROSTER = UNIT_MGR_FLAGS.STRONGHOLD
    TOURNAMENT_ROSTER = UNIT_MGR_FLAGS.TOURNAMENT
    EPIC_ROSTER = UNIT_MGR_FLAGS.SQUAD | UNIT_MGR_FLAGS.EPIC
    BATTLE_ROYALE_ROSTER = UNIT_MGR_FLAGS.SQUAD | UNIT_MGR_FLAGS.BATTLE_ROYALE
    MAPBOX_ROSTER = UNIT_MGR_FLAGS.MAPBOX | UNIT_MGR_FLAGS.SQUAD
    FUN_RANDOM_ROSTER = UNIT_MGR_FLAGS.FUN_RANDOM | UNIT_MGR_FLAGS.SQUAD
    COMP7_ROSTER = UNIT_MGR_FLAGS.SQUAD | UNIT_MGR_FLAGS.COMP7
    _MASK = SQUAD_ROSTER | SPEC_ROSTER | UNIT_MGR_FLAGS.FALLOUT_CLASSIC | UNIT_MGR_FLAGS.FALLOUT_MULTITEAM | UNIT_MGR_FLAGS.EVENT | STRONGHOLD_ROSTER | TOURNAMENT_ROSTER | UNIT_MGR_FLAGS.EPIC | UNIT_MGR_FLAGS.BATTLE_ROYALE | UNIT_MGR_FLAGS.MAPBOX | UNIT_MGR_FLAGS.FUN_RANDOM | COMP7_ROSTER


class EXTRAS_HANDLER_TYPE:
    EMPTY = 0
    SQUAD = 4
    SPEC_BATTLE = 5
    EXTERNAL = 6


class UnitPlayerDataKey(object):
    ACCOUNT_ID = 'accountID'
    ACCOUNT = 'account'
    NICKNAME = 'nickName'
    BADGES = 'badges'
    ROLE = 'role'
    OFFLINE = 'offline'
    IGRTYPE = 'igrType'
    PERIPHERY_ID = 'peripheryID'
    TIME_JOIN = 'timeJoin'
    RATING = 'rating'
    BATTLES_COUNT = 'battlesCount'
    MATCHMAKER_STATS = 'matchmakerStats'
    MAP_BLACKLIST = 'mapBlackList'
    ACCOUNT_WTR = 'accountWTR'
    HAS_WINBACK_TOKEN = 'hasWinbackToken'
    CSR_RATING = 'CSRRating'
    CLAN_DBID = 'clanDBID'
    CLAN_ABBREV = 'clanAbbrev'
    CLAN_NAME = 'clanName'
    CLAN_ROLE = 'clanRole'
    IS_PREMIUM = 'isPremium'
    VEH_DICT = 'vehDict'
    VEH_BATTLES_COUNT = 'vehBattlesCount'
    EXTRA_DATA = 'extraData'


PREBATTLE_TYPE_BY_UNIT_MGR_ROSTER = {PREBATTLE_TYPE.UNIT: UNIT_MGR_FLAGS.DEFAULT,
 PREBATTLE_TYPE.EVENT: ROSTER_TYPE.EVENT_ROSTER,
 PREBATTLE_TYPE.EPIC: ROSTER_TYPE.EPIC_ROSTER,
 PREBATTLE_TYPE.BATTLE_ROYALE: ROSTER_TYPE.BATTLE_ROYALE_ROSTER,
 PREBATTLE_TYPE.MAPBOX: ROSTER_TYPE.MAPBOX_ROSTER,
 PREBATTLE_TYPE.COMP7: ROSTER_TYPE.COMP7_ROSTER}
PREBATTLE_TYPE_BY_UNIT_MGR_ROSTER_EXT = {PREBATTLE_TYPE.SQUAD: ROSTER_TYPE.SQUAD_ROSTER,
 PREBATTLE_TYPE.EVENT: ROSTER_TYPE.EVENT_ROSTER,
 PREBATTLE_TYPE.EPIC: ROSTER_TYPE.EPIC_ROSTER,
 PREBATTLE_TYPE.BATTLE_ROYALE: ROSTER_TYPE.BATTLE_ROYALE_ROSTER,
 PREBATTLE_TYPE.MAPBOX: ROSTER_TYPE.MAPBOX_ROSTER,
 PREBATTLE_TYPE.COMP7: ROSTER_TYPE.COMP7_ROSTER}
QUEUE_TYPE_BY_UNIT_MGR_ROSTER = {QUEUE_TYPE.EVENT_BATTLES: ROSTER_TYPE.EVENT_ROSTER}
ROSTER_TYPE_TO_CLASS = {ROSTER_TYPE.UNIT_ROSTER: UnitRoster,
 ROSTER_TYPE.SQUAD_ROSTER: SquadRoster,
 ROSTER_TYPE.SPEC_ROSTER: SpecRoster,
 ROSTER_TYPE.EVENT_ROSTER: EventRoster,
 ROSTER_TYPE.STRONGHOLD_ROSTER: SpecRoster,
 ROSTER_TYPE.TOURNAMENT_ROSTER: SpecRoster,
 ROSTER_TYPE.EPIC_ROSTER: EpicRoster,
 ROSTER_TYPE.BATTLE_ROYALE_ROSTER: BattleRoyaleRoster,
 ROSTER_TYPE.MAPBOX_ROSTER: MapBoxRoster,
 ROSTER_TYPE.COMP7_ROSTER: Comp7Roster}
EXTRAS_HANDLER_TYPE_TO_HANDLER = {EXTRAS_HANDLER_TYPE.EMPTY: EmptyExtrasHandler,
 EXTRAS_HANDLER_TYPE.SQUAD: SquadExtrasHandler,
 EXTRAS_HANDLER_TYPE.SPEC_BATTLE: ClanBattleExtrasHandler,
 EXTRAS_HANDLER_TYPE.EXTERNAL: ExternalExtrasHandler}

class UnitBase(OpsUnpacker):
    _opsFormatDefs = initOpsFormatDef({UNIT_OP.SET_VEHICLE: ('qIi', '_setVehicle'),
     UNIT_OP.SET_MEMBER: ('qB', '_setMember'),
     UNIT_OP.DEL_MEMBER: ('B', '_delMemberBySlot'),
     UNIT_OP.ADD_PLAYER: ('', '_unpackPlayer'),
     UNIT_OP.REMOVE_PLAYER: ('q', '_removePlayer'),
     UNIT_OP.READY_MASK: ('H', '_setReadyMask'),
     UNIT_OP.SET_SLOT: ('', '_unpackRosterSlot'),
     UNIT_OP.CLEAR_VEHICLE: ('q', '_clearVehicle'),
     UNIT_OP.VEHICLE_DICT: ('', '_unpackVehicleDict'),
     UNIT_OP.UNIT_FLAGS: ('H', '_setUnitFlags'),
     UNIT_OP.CLOSE_SLOT: ('B', '_closeSlot'),
     UNIT_OP.OPEN_SLOT: ('B', '_openSlot'),
     UNIT_OP.SET_COMMENT: ('',
                           'setComment',
                           'S',
                           ['']),
     UNIT_OP.CHANGE_ROLE: ('qH', '_changePlayerRole'),
     UNIT_OP.MODAL_TIMESTAMP: ('i', '_setModalTimestamp'),
     UNIT_OP.GIVE_LEADERSHIP: ('Q', '_giveLeadership'),
     UNIT_OP.EXTRAS_UPDATE: ('',
                             'updateUnitExtras',
                             'S',
                             ['']),
     UNIT_OP.EXTRAS_RESET: (None, 'resetExtras'),
     UNIT_OP.GAMEPLAYS_MASK: ('i', '_setGameplaysMask'),
     UNIT_OP.SET_VEHICLE_LIST: ('q',
                                '_setVehicleList',
                                'N',
                                [('H', 'iI')]),
     UNIT_OP.ARENA_TYPE: ('i', '_setArenaType'),
     UNIT_OP.SET_PLAYER_PROFILE: ('', '_setProfileVehicleByData'),
     UNIT_OP.DEL_PLAYER_PROFILE: ('q', '_delProfileVehicle'),
     UNIT_OP.ESTIMATED_TIME_IN_QUEUE: ('i', '_setEstimatedTimeInQueue'),
     UNIT_OP.ONLY_10_MODE: ('?', '_setOnly10Mode'),
     UNIT_OP.SQUAD_SIZE: ('i', '_setSquadSize'),
     UNIT_OP.SET_SEARCH_FLAGS: ('qH', 'setAutoSearchFlags'),
     UNIT_OP.CLEAR_SEARCH_FLAGS: (None, 'clearAutoSearchFlags'),
     UNIT_OP.REMOVE_SEARCH_FLAGS: ('H', 'removeAutoSearchFlags')})
    MAX_PLAYERS = 250

    def __init__(self, limitsDefs={}, slotDefs={}, slotCount=0, packedRoster='', extrasInit=None, packedUnit='', rosterTypeID=ROSTER_TYPE.UNIT_ROSTER, extrasHandlerID=EXTRAS_HANDLER_TYPE.EMPTY, prebattleTypeID=PREBATTLE_TYPE.UNIT):
        if packedUnit:
            self.unpack(packedUnit)
        else:
            self._rosterTypeID = rosterTypeID
            RosterType = ROSTER_TYPE_TO_CLASS.get(rosterTypeID)
            if slotDefs and not slotCount:
                slotCount = len(slotDefs)
            self._roster = RosterType(limitsDefs, slotDefs, slotCount, packedRoster)
            self._prebattleTypeID = prebattleTypeID
            self._freeSlots = set(xrange(0, slotCount))
            self._dirty = 1
            self._flags = UNIT_FLAGS.DEFAULT
            self._extrasHandlerID = extrasHandlerID
            eHandler = self._initExtrasHandler()
            self._extras = eHandler.new(initial=extrasInit)
            self._initClean()

    def _initClean(self):
        self._members = {}
        self._vehicles = {}
        self._players = {}
        self._playerSlots = {}
        self._playerProfileVehicles = {}
        self._readyMask = 0
        self._gameplaysMask = 0
        self._arenaType = 0
        self._fullReadyMask = 0
        self._strComment = ''
        self._packedOps = ''
        self._packedCmdrOps = ''
        self._closedSlotMask = 0
        self._notifications = []
        self._reservedSlots = set()
        self._modalTimestamp = 0
        self._estimatedTimeInQueue = 0
        self._isOnly10ModeEnabled = False
        self._squadSize = 0
        self._unitAssemblerSearchFlags = {}

    def _initExtrasHandler(self):
        weakSelf = weakref.proxy(self)
        eHnd = self.__extrasHandler = EXTRAS_HANDLER_TYPE_TO_HANDLER[self._extrasHandlerID](weakSelf)
        return eHnd

    @property
    def _extrasHandler(self):
        return self.__extrasHandler

    def _setVehicle(self, accountDBID, vehTypeCompDescr, vehInvID):
        return self._setVehicleList(accountDBID, [(vehInvID, vehTypeCompDescr)])

    def _setVehicleList(self, accountDBID, vehShortList):
        vehs = []
        vehInvIDs = []
        vehTypeCompDescrs = []
        for vehInvID, vehTypeCompDescr in vehShortList:
            classTag = vehicles.getVehicleClass(vehTypeCompDescr)
            vehType = vehicles.getVehicleType(vehTypeCompDescr)
            vehClassIdx = VEHICLE_CLASS_INDICES.get(classTag, _BAD_CLASS_INDEX)
            vehTuple = UnitVehicle(vehInvID, vehTypeCompDescr, vehType.level, vehClassIdx)
            vehs.append(vehTuple)
            vehInvIDs.append(vehInvID)
            vehTypeCompDescrs.append(vehTypeCompDescr)

        self._vehicles[accountDBID] = vehs
        self._autoSelectProfileVehicle(accountDBID, vehs)
        self.storeOp(UNIT_OP.SET_VEHICLE_LIST, accountDBID, vehShortList)
        self._storeNotification(accountDBID, UNIT_NOTIFY_CMD.SET_VEHICLE_LIST, [vehInvIDs])
        self._storeNotification(UNIT_NOTIFY_ID.PARENT_UNIT_MGR, UNIT_NOTIFY_CMD.UPD_VEHICLE_DESCRS, [accountDBID, vehTypeCompDescrs])
        self._dirty = 1
        return True

    def _clearVehicle(self, accountDBID):
        self._vehicles.pop(accountDBID, None)
        self._playerProfileVehicles.pop(accountDBID, None)
        slotIdx = self._playerSlots.get(accountDBID)
        if slotIdx is not None:
            self.setMemberReady(accountDBID, False)
        self._dirty = 1
        self.storeOp(UNIT_OP.CLEAR_VEHICLE, accountDBID)
        self._storeNotification(accountDBID, UNIT_NOTIFY_CMD.SET_VEHICLE_LIST, [[]])
        self._storeNotification(UNIT_NOTIFY_ID.PARENT_UNIT_MGR, UNIT_NOTIFY_CMD.UPD_VEHICLE_DESCRS, [accountDBID, []])
        return

    def _setMember(self, accountDBID, slotChosenIdx):
        member = dict(accountDBID=accountDBID, slotIdx=slotChosenIdx)
        self.__updateReadyMask(accountDBID, slotChosenIdx)
        self._members.pop(self._playerSlots.get(accountDBID), None)
        self._members[slotChosenIdx] = member
        self._freeSlots.discard(slotChosenIdx)
        self._playerSlots[accountDBID] = slotChosenIdx
        self._fullReadyMask |= 1 << slotChosenIdx
        self.storeOp(UNIT_OP.SET_MEMBER, accountDBID, slotChosenIdx)
        self._dirty = 1
        return

    def __updateReadyMask(self, accountDBID, newSlotIdx):
        currentSlotIdx = self._playerSlots.get(accountDBID)
        if currentSlotIdx is not None and currentSlotIdx != newSlotIdx:
            if self.isMemberReady(accountDBID):
                self._readyMask |= 1 << newSlotIdx
            else:
                self._readyMask &= ~(1 << newSlotIdx)
            self._readyMask &= ~(1 << currentSlotIdx)
            self._fullReadyMask &= ~(1 << currentSlotIdx)
        return

    def _delMemberBySlot(self, slotIdx):
        member = self._members.get(slotIdx, None)
        if not member:
            return UNIT_ERROR.FAIL_UNIT_METHOD
        else:
            accountDBID = member['accountDBID']
            self.setMemberReady(accountDBID, False)
            self._members.pop(slotIdx)
            self._freeSlots.add(slotIdx)
            self._playerSlots.pop(accountDBID, None)
            clearMask = ~(1 << slotIdx)
            self._fullReadyMask &= clearMask
            self._dirty = 1
            self.storeOp(UNIT_OP.DEL_MEMBER, slotIdx)
            return OK

    def _autoSelectProfileVehicle(self, accountDBID, vehicles):
        pass

    def _setProfileVehicle(self, accountDBID, vehCompDescr, vehOutfitCD, seasonType, marksOnGun):
        LOG_DEBUG('_setProfileVehicle: accountDBID={}'.format(accountDBID))
        newProfileVehicle = ProfileVehicle(vehCompDescr, vehOutfitCD, seasonType, marksOnGun)
        if newProfileVehicle != self._playerProfileVehicles.get(accountDBID, None):
            self._playerProfileVehicles[accountDBID] = newProfileVehicle
            self._dirty = 1
            packed = self.__packProfileVehicle(accountDBID, newProfileVehicle)
            self._appendOp(UNIT_OP.SET_PLAYER_PROFILE, packed)
        return

    def _delProfileVehicle(self, accountDBID):
        LOG_DEBUG('_delProfileVehicle: accountDBID={}'.format(accountDBID))
        self._playerProfileVehicles.pop(accountDBID, None)
        self.storeOp(UNIT_OP.DEL_PLAYER_PROFILE, accountDBID)
        return

    def _setProfileVehicleByData(self, packedOps):
        profileLen = self.__unpackProfileVehicle(packedOps)
        return packedOps[profileLen:]

    def _setEstimatedTimeInQueue(self, estimatedTimeInQueue):
        LOG_DEBUG_DEV('_setEstimatedTimeInQueue %d' % estimatedTimeInQueue)
        self._estimatedTimeInQueue = estimatedTimeInQueue
        self.storeOp(UNIT_OP.ESTIMATED_TIME_IN_QUEUE, estimatedTimeInQueue)
        self._dirty = 1

    def _addPlayer(self, accountDBID, **kwargs):
        self._players[accountDBID] = kwargs
        self._dirty = 1
        packed = self.__packPlayerData(accountDBID, **kwargs)
        self._appendOp(UNIT_OP.ADD_PLAYER, packed)

    def _removePlayer(self, accountDBID):
        self._players.pop(accountDBID, None)
        self._vehicles.pop(accountDBID, None)
        self._unitAssemblerSearchFlags.pop(accountDBID, None)
        self._playerProfileVehicles.pop(accountDBID, None)
        self._dirty = 1
        self.storeOp(UNIT_OP.REMOVE_PLAYER, accountDBID)
        return

    def _changePlayerRole(self, accountDBID, roleFlags):
        playerData = self._players.get(accountDBID)
        if playerData:
            playerData['role'] = roleFlags
            self._dirty = 1
            self.storeOp(UNIT_OP.CHANGE_ROLE, accountDBID, roleFlags)

    def _setRosterSlot(self, rosterSlotIdx, packedSlot):
        packedArgs = struct.pack('<B', rosterSlotIdx)
        packedArgs += packedSlot
        slot = self._roster.SLOT_TYPE(packed=packedSlot)
        roster = self._roster
        if slot.vehTypeCompDescr is None and slot.nationMask == 0 and slot.vehClassMask == 0:
            roster.slots.pop(rosterSlotIdx, None)
        else:
            neighbourSlotIdx = rosterSlotIdx ^ 1
            neighbourSlot = roster.slots.get(neighbourSlotIdx)
            if neighbourSlot and packedSlot == roster.DEFAULT_SLOT_PACK:
                LOG_DEBUG('_setRosterSlot: removing default slotIdx=%s' % rosterSlotIdx)
                roster.slots.pop(rosterSlotIdx, None)
            else:
                roster.slots[rosterSlotIdx] = slot
                if neighbourSlot and neighbourSlot.pack() == roster.DEFAULT_SLOT_PACK:
                    LOG_DEBUG('_setRosterSlot: removing default neighbour slotIdx=%s' % rosterSlotIdx)
                    roster.slots.pop(neighbourSlotIdx, None)
        roster.pack()
        self._dirty = 1
        self._appendOp(UNIT_OP.SET_SLOT, packedArgs)
        return

    def isEmpty(self):
        for accountDBID, playerInfo in self._players.iteritems():
            role = playerInfo.get('role', 0)
            if role & UNIT_ROLE.INVITED == 0:
                return False

        return True

    _HEADER = '<HHHHHHHHBiiii?i'
    _PLAYER_DATA = '<qiIHBHHHq?'
    _PLAYER_VEHICLES_LIST = '<qH'
    _PLAYER_VEHICLE_TUPLE = '<iI'
    _SLOT_PLAYERS = '<Bq'
    _IDS = '<IBB'
    _VEHICLE_DICT_HEADER = '<Hq'
    _VEHICLE_DICT_ITEM = '<Ii'
    _VEHICLE_PROFILE_HEADER = '<qBB'
    _PLAYER_SEARCH_FLAGS_TUPLE = '<qH'
    _HEADER_SIZE = struct.calcsize(_HEADER)
    _SLOT_PLAYERS_SIZE = struct.calcsize(_SLOT_PLAYERS)
    _PLAYER_DATA_SIZE = struct.calcsize(_PLAYER_DATA)
    _PLAYER_VEHICLES_LIST_SIZE = struct.calcsize(_PLAYER_VEHICLES_LIST)
    _PLAYER_VEHICLE_TUPLE_SIZE = struct.calcsize(_PLAYER_VEHICLE_TUPLE)
    _IDS_SIZE = struct.calcsize(_IDS)
    _VEHICLE_DICT_HEADER_SIZE = struct.calcsize(_VEHICLE_DICT_HEADER)
    _VEHICLE_DICT_ITEM_SIZE = struct.calcsize(_VEHICLE_DICT_ITEM)
    _VEHICLE_PROFILE_HEADER_SIZE = struct.calcsize(_VEHICLE_PROFILE_HEADER)
    _PLAYER_SEARCH_FLAGS_TUPLE_SIZE = struct.calcsize(_PLAYER_SEARCH_FLAGS_TUPLE)

    def pack(self):
        packed = struct.pack(self._IDS, self._rosterTypeID, self._extrasHandlerID, self._prebattleTypeID)
        packed += self._roster.getPacked()
        members = self._members
        players = self._players
        vehs = self._vehicles
        extras = self._extras
        extrasStr = self._extrasHandler.pack(extras)
        profileVehicles = self._playerProfileVehicles
        searchFlags = self._unitAssemblerSearchFlags
        args = (len(members),
         len(vehs),
         len(players),
         len(profileVehicles),
         len(searchFlags),
         len(extrasStr),
         self._readyMask,
         self._flags,
         self._closedSlotMask,
         self._modalTimestamp,
         self._estimatedTimeInQueue,
         self._gameplaysMask,
         self._arenaType,
         self._isOnly10ModeEnabled,
         self._squadSize)
        packed += struct.pack(self._HEADER, *args)
        for accountDBID, vehList in vehs.iteritems():
            packed += struct.pack(self._PLAYER_VEHICLES_LIST, accountDBID, len(vehList))
            for vehTuple in vehList:
                packed += struct.pack(self._PLAYER_VEHICLE_TUPLE, vehTuple.vehInvID, vehTuple.vehTypeCompDescr)

        for slotIdx, member in members.iteritems():
            packed += struct.pack(self._SLOT_PLAYERS, slotIdx, member['accountDBID'])

        for accountDBID, playerData in players.iteritems():
            packed += self.__packPlayerData(accountDBID, **playerData)

        for accountDBID, profileVehicle in profileVehicles.iteritems():
            packed += self.__packProfileVehicle(accountDBID, profileVehicle)

        for accountDBID, searchFlags in searchFlags.iteritems():
            packed += struct.pack(self._PLAYER_SEARCH_FLAGS_TUPLE, accountDBID, searchFlags)

        packed += extrasStr
        packed += packPascalString(self._strComment)
        self._packed = packed
        self._dirty = 0
        return packed

    def unpack(self, packed):
        self._initClean()
        self._rosterTypeID, self._extrasHandlerID, self._prebattleTypeID = struct.unpack_from(self._IDS, packed)
        RosterType = ROSTER_TYPE_TO_CLASS.get(self._rosterTypeID)
        self._roster = RosterType()
        self._initExtrasHandler()
        unpacking = packed[self._IDS_SIZE:]
        unpacking = self._roster.unpack(unpacking)
        slotCount = self.getMaxSlotCount()
        self._freeSlots = set(xrange(0, slotCount))
        memberCount, vehCount, playerCount, profilesCount, searchFlagsCount, extrasLen, self._readyMask, self._flags, self._closedSlotMask, self._modalTimestamp, self._estimatedTimeInQueue, self._gameplaysMask, self._arenaType, self._isOnly10ModeEnabled, self._squadSize = struct.unpack_from(self._HEADER, unpacking)
        unpacking = unpacking[self._HEADER_SIZE:]
        for i in xrange(0, vehCount):
            accountDBID, vehListCount = struct.unpack_from(self._PLAYER_VEHICLES_LIST, unpacking)
            unpacking = unpacking[self._PLAYER_VEHICLES_LIST_SIZE:]
            vehDataList = []
            for i in xrange(0, vehListCount):
                vehInvID, vehTypeCompDescr = struct.unpack_from(self._PLAYER_VEHICLE_TUPLE, unpacking)
                unpacking = unpacking[self._PLAYER_VEHICLE_TUPLE_SIZE:]
                vehDataList.append((vehInvID, vehTypeCompDescr))

            self._setVehicleList(accountDBID, vehDataList)

        for i in xrange(0, memberCount):
            slotIdx, accountDBID = struct.unpack_from(self._SLOT_PLAYERS, unpacking)
            self._setMember(accountDBID, slotIdx)
            unpacking = unpacking[self._SLOT_PLAYERS_SIZE:]

        for i in xrange(0, playerCount):
            blockLength, accountDBID, accountID, timeJoin, role, igrType, rating, accountWTR, peripheryID, clanDBID, isPremium, nickName, clanAbbrev, badges, extraData = self.__unpackPlayerData(unpacking)
            unpacking = unpacking[blockLength:]
            playerData = {UnitPlayerDataKey.ACCOUNT_ID: accountID,
             UnitPlayerDataKey.TIME_JOIN: timeJoin,
             UnitPlayerDataKey.ROLE: role,
             UnitPlayerDataKey.RATING: rating,
             UnitPlayerDataKey.ACCOUNT_WTR: accountWTR,
             UnitPlayerDataKey.NICKNAME: nickName,
             UnitPlayerDataKey.CLAN_DBID: clanDBID,
             UnitPlayerDataKey.CLAN_ABBREV: clanAbbrev,
             UnitPlayerDataKey.PERIPHERY_ID: peripheryID,
             UnitPlayerDataKey.IGRTYPE: igrType,
             UnitPlayerDataKey.BADGES: badges,
             UnitPlayerDataKey.IS_PREMIUM: isPremium,
             UnitPlayerDataKey.EXTRA_DATA: extraData}
            self._addPlayer(accountDBID, **playerData)

        for i in xrange(0, profilesCount):
            profileLen = self.__unpackProfileVehicle(unpacking)
            unpacking = unpacking[profileLen:]

        for i in xrange(0, searchFlagsCount):
            accountDBID, searchFlags = struct.unpack_from(self._PLAYER_SEARCH_FLAGS_TUPLE, unpacking)
            self.setAutoSearchFlags(accountDBID, searchFlags)
            unpacking = unpacking[self._PLAYER_SEARCH_FLAGS_TUPLE_SIZE:]

        self._extras = self._extrasHandler.unpack(unpacking[:extrasLen])
        unpacking = unpacking[extrasLen:]
        for slotIdx in range(0, 7):
            slotMask = 1 << slotIdx
            if self._closedSlotMask & slotMask:
                self._closeSlot(slotIdx)

        self._strComment, lenCommentBytes = unpackPascalString(unpacking)
        unpacking = unpacking[lenCommentBytes:]
        lengthDiff = len(packed) - len(unpacking)
        self._packed = packed[:lengthDiff]
        self._packedOps = ''
        self._dirty = 0
        return unpacking

    def isDirty(self):
        return self._dirty

    def getCommanderDBID(self):
        return self._members.get(LEADER_SLOT, {}).get('accountDBID', 0)

    def getAccountsStates(self):
        statesDict = {}
        assignedPlayers = self._playerSlots.keys()
        accountsVehicles = self._vehicles
        isMemberReadyFunc = self.isMemberReady
        for accountDBID, playerData in self._players.iteritems():
            vehs = accountsVehicles.get(accountDBID)
            statesDict[accountDBID] = (vehs[0].vehTypeCompDescr if vehs else None, accountDBID in assignedPlayers, isMemberReadyFunc(accountDBID))

        return statesDict

    def updateUnitExtras(self, updateStr):
        oldExtras = copy.deepcopy(self._extras)
        self._extrasHandler.updateUnitExtras(self._extras, updateStr)
        newExtras = self._extras
        LOG_DEBUG_DEV('updateUnitExtras', oldExtras, newExtras)
        self.storeOp(UNIT_OP.EXTRAS_UPDATE, updateStr)
        for accountDBID, playerData in self._players.iteritems():
            if playerData and playerData.get('role', 0) & UNIT_ROLE.INVITED == 0:
                self._storeNotification(accountDBID, UNIT_NOTIFY_CMD.EXTRAS_UPDATED, [newExtras])

        self._storeNotification(UNIT_NOTIFY_ID.PARENT_UNIT_MGR, UNIT_NOTIFY_CMD.EXTRAS_UPDATED, [oldExtras, newExtras])
        self._dirty = 1

    def getPacked(self):
        if self._dirty:
            return self.pack()
        else:
            return self._packed

    def isReady(self):
        readyMask = self._readyMask
        return readyMask == self._fullReadyMask and readyMask

    def anyReady(self):
        return bool(self._readyMask)

    def isLocked(self):
        return bool(self._flags & UNIT_FLAGS.LOCKED)

    def isInviteOnly(self):
        return bool(self._flags & UNIT_FLAGS.INVITE_ONLY)

    def isIdle(self):
        return self._flags & UNIT_FLAGS.MODAL_STATES == 0

    def isDevMode(self):
        return bool(self._flags & UNIT_FLAGS.DEV_MODE)

    def isInQueue(self):
        return bool(self._flags & UNIT_FLAGS.IN_QUEUE)

    def isInSearch(self):
        return bool(self._flags & UNIT_FLAGS.IN_SEARCH)

    def isFinishAssembling(self):
        return bool(self._flags & UNIT_FLAGS.FINISH_ASSEMBLING)

    def isInArena(self):
        return bool(self._flags & UNIT_FLAGS.IN_ARENA)

    def isSortiesForbidden(self):
        return bool(self._flags & UNIT_FLAGS.SORTIES_FORBIDDEN)

    def isDynamic(self):
        return bool(self._flags & UNIT_FLAGS.IS_DYNAMIC)

    def isSquad(self):
        return bool(self._rosterTypeID & UNIT_MGR_FLAGS.SQUAD)

    def shouldPublish(self):
        return not (self.isInviteOnly() or self.isSortiesForbidden())

    def __repr__(self):
        repr = 'Unit(\n  _members len=%s {' % len(self._members)
        for slotIdx, member in self._members.iteritems():
            repr += '\n    [%d] %s' % (slotIdx, member)

        repr += '\n  },'
        repr += '\n  state=0x%02X, readyMask=0x%02X, fullReadyMask=0x%02X, closedSlotMask=0x%02X' % (self._flags,
         self._readyMask,
         self._fullReadyMask,
         self._closedSlotMask)
        repr += '\n  state(names):%s' % reprBitMaskFromDict(self._flags, UNIT_STATE_NAMES)
        repr += '\n  modalTimestamp:%s' % self._modalTimestamp
        repr += '\n  estimatedTimeInQueue:%s' % self._estimatedTimeInQueue
        repr += '\n  _vehicles len=%s {' % len(self._vehicles)
        for accountDBID, veh in self._vehicles.iteritems():
            repr += '\n    [%d] %s' % (accountDBID, str(veh))

        repr += '\n  },'
        repr += '\n  _players len=%s {' % len(self._players)
        for accountDBID, playerData in self._players.iteritems():
            repr += '\n    [%d] %s role=%s' % (accountDBID, playerData, reprBitMaskFromDict(playerData.get('role', 0), UNIT_ROLE_NAMES))

        repr += '\n  },'
        repr += '\n  _freeSlots=%r,' % self._freeSlots
        repr += '\n  _roster=%r' % self._roster
        repr += '\n _extras=%r' % self._extras
        repr += '\n  _strComment=%r' % self._strComment
        repr += '\n)'
        return repr

    def dump(self):
        repr = 'Unit(\n membs(%s)={' % len(self._members)
        for slotIdx, member in self._members.iteritems():
            repr += '%d:%s, ' % (slotIdx, member.get('accountDBID', 0))

        repr += '},'
        repr += '\n state=%02X, rdy=%02X, fullRdy=%02X, closed=%02X' % (self._flags,
         self._readyMask,
         self._fullReadyMask,
         self._closedSlotMask)
        repr += ', stamp:%s, timeInQueue:%d, free=%r' % (self._modalTimestamp, self._estimatedTimeInQueue, list(self._freeSlots))
        repr += '\n vehs(%s)={' % len(self._vehicles)
        for accountDBID, veh in self._vehicles.iteritems():
            repr += '%d:%s, ' % (accountDBID, str(veh))

        repr += '},'
        repr += '\n plrs(%s)={' % len(self._players)
        for accountDBID, playerData in self._players.iteritems():
            repr += '%d:%r:%02X, ' % (accountDBID, playerData.get('nickName', ''), playerData.get('role', 0))

        repr += '},'
        repr += '\n roster=%r' % self._roster.getPacked()
        repr += '\n extras=%r' % self._extras
        repr += '\n)'
        return repr

    def setMemberReady(self, accountDBID, isReady=True):
        slotIdx = self._playerSlots.get(accountDBID)
        if slotIdx is None:
            return UNIT_ERROR.BAD_SLOT_IDX
        elif isReady and not self._isValidMember(accountDBID):
            return UNIT_ERROR.INVALID_ACCOUNT
        else:
            prevReadyMask = self._readyMask
            if isReady:
                vehs = self._vehicles.get(accountDBID)
                if vehs is None:
                    return UNIT_ERROR.VEHICLE_NOT_CHOSEN
                vehList = [ (vehicle.vehInvID, vehicle.vehTypeCompDescr) for vehicle in vehs ]
                if not self._canUseVehicles(vehList):
                    return UNIT_ERROR.BAD_VEHICLES_SET
                newReadyMask = prevReadyMask | 1 << slotIdx
            else:
                newReadyMask = prevReadyMask & ~(1 << slotIdx)
            if newReadyMask != prevReadyMask:
                self._readyMask = newReadyMask
                self.storeOp(UNIT_OP.READY_MASK, newReadyMask)
                self._dirty = 1
                self._storeNotification(accountDBID, UNIT_NOTIFY_CMD.SET_MEMBER_READY, [isReady])
            return OK

    def setAutoSearchFlags(self, accountDBID, flags):
        if self._unitAssemblerSearchFlags.get(accountDBID, None) != flags:
            self._unitAssemblerSearchFlags[accountDBID] = flags
            self.storeOp(UNIT_OP.SET_SEARCH_FLAGS, accountDBID, flags)
        return

    def removeAutoSearchFlags(self, flags):
        anyChange = False
        for k, v in self._unitAssemblerSearchFlags.iteritems():
            self._unitAssemblerSearchFlags[k] &= ~flags
            anyChange = True

        if anyChange:
            self.storeOp(UNIT_OP.REMOVE_SEARCH_FLAGS, flags)

    def clearAutoSearchFlags(self):
        if self._unitAssemblerSearchFlags:
            self._unitAssemblerSearchFlags.clear()
            self.storeOp(UNIT_OP.CLEAR_SEARCH_FLAGS)

    def getAutoSearchFlags(self):
        numSearchFlags = len(self._unitAssemblerSearchFlags)
        if numSearchFlags == 0:
            return UnitAssemblerSearchFlags.NO_FILTER
        if numSearchFlags == 1:
            return self._unitAssemblerSearchFlags.values()[0]
        tankFilter = 0
        for userFilter in self._unitAssemblerSearchFlags.itervalues():
            tankFilter |= userFilter

        for userFilter in self._unitAssemblerSearchFlags.itervalues():
            if userFilter & UnitAssemblerSearchFlags.ALL_VEH_TIERS != 0:
                tankFilter &= userFilter

        tankFilter &= UnitAssemblerSearchFlags.ALL_VEH_TIERS
        commanderFilter = self._unitAssemblerSearchFlags.get(self.getCommanderDBID(), 0)
        if tankFilter == 0:
            tankFilter = commanderFilter
        commanderOverrideMask = UnitAssemblerSearchFlags.USE_VOICE | UnitAssemblerSearchFlags.DESTROY_UNIT_ON_ABORT
        searchFlags = tankFilter | commanderFilter & commanderOverrideMask
        return searchFlags

    def hasAutoSearchFlags(self, flags):
        return self.getAutoSearchFlags() & flags == flags

    def getAutoSearchFlagsOfAccount(self, accountDBID):
        return self._unitAssemblerSearchFlags.get(accountDBID, 0)

    def _canUseVehicles(self, vehiclesList, isSet=False, isCommanderSet=False):
        return True

    def _setGameplaysMask(self, newGameplaysMask):
        prevGameplaysMask = self._gameplaysMask
        if prevGameplaysMask != newGameplaysMask:
            self._gameplaysMask = newGameplaysMask
            self.storeOp(UNIT_OP.GAMEPLAYS_MASK, newGameplaysMask)
        return OK

    def _setOnly10Mode(self, newIsOnly10Mode):
        isOnly10ModeEnabled = self._isOnly10ModeEnabled
        if isOnly10ModeEnabled != newIsOnly10Mode:
            self._isOnly10ModeEnabled = newIsOnly10Mode
            self.storeOp(UNIT_OP.ONLY_10_MODE, newIsOnly10Mode)
        return OK

    def _setSquadSize(self, newSquadSize):
        LOG_DEBUG_DEV('_setSquadSize', newSquadSize, len(self._players), self._squadSize)
        if len(self._players) > newSquadSize:
            return UNIT_ERROR.BAD_PARAMS
        else:
            squadSize = self._squadSize
            if squadSize != newSquadSize or self._freeSlots > squadSize:
                playerSlotsIterator = iter(sorted(self._playerSlots.iteritems(), key=lambda x: x[1]))
                for squadSlotIdx in xrange(newSquadSize):
                    accountDBID, prevSlotIdx = next(playerSlotsIterator, (None, None))
                    if squadSlotIdx == LEADER_SLOT:
                        continue
                    if accountDBID and prevSlotIdx != squadSlotIdx:
                        self._setMember(accountDBID, squadSlotIdx)

                self._refreshFreeSlots(squadSize, newSquadSize)
                self._squadSize = newSquadSize
                self.storeOp(UNIT_OP.SQUAD_SIZE, newSquadSize)
                for accountDBID, _ in self._players.iteritems():
                    self._storeNotification(accountDBID, UNIT_NOTIFY_CMD.CHANGE_SQUAD_SIZE, [newSquadSize, bool(self._freeSlots)])

                self._dirty = 1
            return OK

    def _setArenaType(self, newArenaType):
        prevArenaType = self._arenaType
        if prevArenaType != newArenaType:
            self._arenaType = newArenaType
            self.storeOp(UNIT_OP.ARENA_TYPE, newArenaType)
        return OK

    def isMemberReady(self, accountDBID):
        slotIdx = self._playerSlots.get(accountDBID)
        return bool(self._readyMask & 1 << slotIdx) if slotIdx is not None else False

    def _setModalTimestamp(self, timestamp):
        self._modalTimestamp = timestamp
        self.storeOp(UNIT_OP.MODAL_TIMESTAMP, timestamp)
        self._dirty = 1

    def _setReadyMask(self, mask):
        self._readyMask = mask

    def _setUnitFlags(self, state):
        self._flags = state

    def _closeSlot(self, slotIdx):
        self._closedSlotMask |= 1 << slotIdx
        self._freeSlots.discard(slotIdx)
        self._dirty = 1
        self.storeOp(UNIT_OP.CLOSE_SLOT, slotIdx)

    def getMaxSlotCount(self):
        if self._roster.slots:
            _max = max(self._roster.slots.iterkeys())
        else:
            _max = 0
        return _max / 2 + 1

    def getClosedSlotsCount(self):
        count = 0
        for i in xrange(self._roster.MAX_SLOTS):
            if self._closedSlotMask & 1 << i:
                count += 1

        return count

    def getPointsSum(self):
        sum = 0
        for slotIdx, member in self._members.iteritems():
            accountDBID = member.get('accountDBID', 0)
            vehs = self._vehicles.get(accountDBID)
            if vehs:
                sum += vehs[0].vehLevel

        return sum

    def checkVehicleLevelsRange(self, lvlsByClass, commonLvls):
        for slotIdx, member in self._members.iteritems():
            accountDBID = member.get('accountDBID', None)
            if accountDBID is None:
                continue
            vehs = self._vehicles.get(accountDBID, None)
            if not vehs:
                continue
            for vehTuple in vehs:
                vehLevel = vehTuple.vehLevel
                levelLimits = commonLvls
                if lvlsByClass is not None:
                    levelLimits = lvlsByClass.get(vehTuple.vehClassIdx, commonLvls)
                if vehLevel < levelLimits[0] or levelLimits[1] < vehLevel:
                    return False

        return True

    def checkVehicleTypesRange(self, vehicleTypes):
        vehicleCount = {}
        for slotIdx, member in self._members.iteritems():
            accountDBID = member.get('accountDBID', None)
            if accountDBID is None:
                continue
            vehs = self._vehicles.get(accountDBID)
            if not vehs:
                continue
            for vehTuple in vehs:
                vehTypeCompDescr = vehTuple.vehTypeCompDescr
                if vehTypeCompDescr is None:
                    continue
                if vehTypeCompDescr not in vehicleTypes:
                    return UNIT_ERROR.BAD_VEHICLE_TYPE
                if vehTypeCompDescr not in vehicleCount:
                    vehicleCount[vehTypeCompDescr] = 0
                vehicleCount[vehTypeCompDescr] += 1

        if any((value < vehicleTypes[key][0] for key, value in vehicleCount.iteritems())):
            return UNIT_ERROR.TOO_FEW_VEHICLE_TYPE
        else:
            return UNIT_ERROR.TOO_MANY_VEHICLE_TYPE if any((value > vehicleTypes[key][1] for key, value in vehicleCount.iteritems())) else OK

    def hasInArenaMembers(self):
        for slotIdx, member in self._members.iteritems():
            accountDBID = member.get('accountDBID', 0)
            role = self.getAccountRole(accountDBID)
            if role & UNIT_ROLE.IN_ARENA:
                return True

        return False

    def getLegionaryCount(self):
        count = 0
        for accountDBID, slotIdx in self._playerSlots.iteritems():
            playerData = self._players[accountDBID]
            role = playerData.get('role', 0)
            if role & UNIT_ROLE.LEGIONARY:
                count += 1

        return count

    def getLegionaryMaxCount(self):
        return self._roster.getLegionariesMaxCount()

    def resetExtras(self):
        self._extras = self._extrasHandler.reset(self._extras)
        self.storeOp(UNIT_OP.EXTRAS_RESET)
        self._dirty = 1

    def _openSlot(self, slotIdx):
        self._closedSlotMask &= ~(1 << slotIdx)
        self._freeSlots.add(slotIdx)
        self._dirty = 1
        self.storeOp(UNIT_OP.OPEN_SLOT, slotIdx)

    def _reserveUnitSlot(self, unitSlotIdx):
        self._reservedSlots.add(unitSlotIdx)
        reservedRosterSlot = self._roster.SLOT_TYPE()
        reservedRosterSlot.vehTypeCompDescr = 0
        for slotIdx in (unitSlotIdx * 2, unitSlotIdx * 2 + 1):
            self._roster.slots[slotIdx] = reservedRosterSlot

    def setComment(self, strComment):
        self._strComment = strComment
        self.storeOp(UNIT_OP.SET_COMMENT, strComment)
        self._dirty = 1
        return OK

    def _appendCmdrOp(self, op, packedArgs):
        pass

    def _storeNotification(self, accountDBID, notifyCmd, argList=[]):
        pass

    def _unpackRosterSlot(self, packedOps):
        rosterSlotIdx = struct.unpack_from('<B', packedOps)[0]
        opLen = BaseUnitRosterSlot.getPackSize(packedOps[1]) + 1
        packedSlot = packedOps[1:opLen]
        self._setRosterSlot(rosterSlotIdx, packedSlot)
        return packedOps[opLen:]

    def _packVehicleDict(self, accountDBID, vehDict={}):
        packedArgs = struct.pack(self._VEHICLE_DICT_HEADER, len(vehDict), accountDBID)
        for vehTypeCompDescr, vehInvID in vehDict.iteritems():
            packedArgs += struct.pack(self._VEHICLE_DICT_ITEM, vehTypeCompDescr, vehInvID)

        self._appendCmdrOp(UNIT_OP.VEHICLE_DICT, packedArgs)

    def _packFullVehDictUpdates(self):
        for accountDBID, playerData in self._players.iteritems():
            if playerData and playerData.get('role', 0) & UNIT_ROLE.INVITED == 0:
                vehDict = playerData.get('vehDict')
                if vehDict:
                    self._packVehicleDict(accountDBID, vehDict)

    def _unpackVehicleDict(self, packedOps):
        vehCount, accountDBID = struct.unpack_from(self._VEHICLE_DICT_HEADER, packedOps)
        vehDict = {}
        opLen = self._VEHICLE_DICT_HEADER_SIZE
        for i in xrange(vehCount):
            vehTypeCompDescr, vehInvID = struct.unpack_from(self._VEHICLE_DICT_ITEM, packedOps, opLen)
            vehDict[vehTypeCompDescr] = vehInvID
            opLen += self._VEHICLE_DICT_ITEM_SIZE

        playerData = self._players.get(accountDBID)
        if playerData:
            playerData['vehDict'] = vehDict
        return packedOps[opLen:]

    def _unpackPlayer(self, packedOps):
        blockLength, accountDBID, accountID, timeJoin, role, igrType, rating, accountWTR, peripheryID, clanDBID, isPremium, nickName, clanAbbrev, badges, extraData = self.__unpackPlayerData(packedOps)
        playerData = {UnitPlayerDataKey.ACCOUNT_ID: accountID,
         UnitPlayerDataKey.TIME_JOIN: timeJoin,
         UnitPlayerDataKey.ROLE: role,
         UnitPlayerDataKey.RATING: rating,
         UnitPlayerDataKey.ACCOUNT_WTR: accountWTR,
         UnitPlayerDataKey.NICKNAME: nickName,
         UnitPlayerDataKey.CLAN_DBID: clanDBID,
         UnitPlayerDataKey.CLAN_ABBREV: clanAbbrev,
         UnitPlayerDataKey.PERIPHERY_ID: peripheryID,
         UnitPlayerDataKey.IGRTYPE: igrType,
         UnitPlayerDataKey.BADGES: badges,
         UnitPlayerDataKey.IS_PREMIUM: isPremium,
         UnitPlayerDataKey.EXTRA_DATA: extraData}
        self._addPlayer(accountDBID, **playerData)
        return packedOps[blockLength:]

    def _giveLeadership(self, newLeaderDBID):
        swapSlotIdx = self._playerSlots.get(newLeaderDBID)
        prevLeaderDBID = self._members[LEADER_SLOT]['accountDBID']
        self.setMemberReady(prevLeaderDBID, False)
        self.setMemberReady(newLeaderDBID, False)
        if swapSlotIdx is not None:
            self._members[swapSlotIdx] = dict(accountDBID=prevLeaderDBID, slotIdx=swapSlotIdx)
            self._playerSlots[prevLeaderDBID] = swapSlotIdx
        else:
            self._playerSlots.pop(prevLeaderDBID)
        self._players[prevLeaderDBID]['role'] &= ~UNIT_ROLE.CREATOR
        self._members[LEADER_SLOT] = dict(accountDBID=newLeaderDBID, slotIdx=LEADER_SLOT)
        self._playerSlots[newLeaderDBID] = LEADER_SLOT
        self._players[newLeaderDBID]['role'] |= UNIT_ROLE.CREATOR
        self.storeOp(UNIT_OP.GIVE_LEADERSHIP, newLeaderDBID)
        return prevLeaderDBID

    def _refreshFreeSlots(self, prevMax, newMax):
        if prevMax > newMax:
            for indx in xrange(newMax, prevMax):
                self._freeSlots.discard(indx)

        elif prevMax < newMax:
            for indx in xrange(prevMax, newMax):
                self._freeSlots.add(indx)

        for idx in self._freeSlots - set(xrange(0, newMax)):
            self._freeSlots.discard(idx)

    def _getLeaderDBID(self):
        return self._members.get(LEADER_SLOT, {}).get('accountDBID', 0)

    def isMultiVehicle(self):
        return self._roster.MAX_VEHICLES > 1

    def getRosterType(self):
        return self._rosterTypeID

    def getSquadSize(self):
        return self._squadSize

    def _isValidMember(self, accountDBID):
        return True

    def _checkAllVehiclesMatchSlot(self, accountDBID, unitSlotIdx):
        vehList = self._vehicles.get(accountDBID, [])
        for veh in vehList:
            res, slotChosenIdx = self._roster.checkVehicle(veh.vehTypeCompDescr, unitSlotIdx)
            if not res:
                return (False, veh.vehInvID)

        return (True, None)

    def _makePlayerExtraDataForClient(self, extraData):
        return {}

    def __packPlayerData(self, accountDBID, **kwargs):
        packed = struct.pack(self._PLAYER_DATA, accountDBID, kwargs.get(UnitPlayerDataKey.ACCOUNT_ID, 0), kwargs.get(UnitPlayerDataKey.TIME_JOIN, 0), kwargs.get(UnitPlayerDataKey.ROLE, 0), kwargs.get(UnitPlayerDataKey.IGRTYPE, 0), kwargs.get(UnitPlayerDataKey.RATING, 0), kwargs.get(UnitPlayerDataKey.ACCOUNT_WTR, 0), kwargs.get(UnitPlayerDataKey.PERIPHERY_ID, 0), kwargs.get(UnitPlayerDataKey.CLAN_DBID, 0), kwargs.get(UnitPlayerDataKey.IS_PREMIUM, False))
        packed += packPascalString(kwargs.get(UnitPlayerDataKey.NICKNAME, ''))
        packed += packPascalString(kwargs.get(UnitPlayerDataKey.CLAN_ABBREV, ''))
        badges = kwargs.get(UnitPlayerDataKey.BADGES, BadgesCommon.selectedBadgesEmpty())
        packed += BadgesCommon.packPlayerBadges(badges)
        packed += self.__packPlayerExtraData(self._makePlayerExtraDataForClient(kwargs.get('extraData', {})))
        return packed

    def __unpackPlayerData(self, packedData):
        sz = self._PLAYER_DATA_SIZE
        accountDBID, accountID, timeJoin, role, igrType, rating, accountWTR, peripheryID, clanDBID, isPremium = struct.unpack_from(self._PLAYER_DATA, packedData)
        offset = sz
        nickName, lenNickBytes = unpackPascalString(packedData, offset)
        offset += lenNickBytes
        clanAbbrev, lenClanBytes = unpackPascalString(packedData, offset)
        offset += lenClanBytes
        badges, lenBadgesInfo = BadgesCommon.unpackPlayerBadges(packedData, offset)
        offset += lenBadgesInfo
        extraData, lenExtraData = self.__unpackPlayerExtraData(packedData, offset)
        offset += lenExtraData
        return (offset,
         accountDBID,
         accountID,
         timeJoin,
         role,
         igrType,
         rating,
         accountWTR,
         peripheryID,
         clanDBID,
         isPremium,
         nickName,
         clanAbbrev,
         badges,
         extraData)

    @staticmethod
    def __packPlayerExtraData(packedData):
        LOG_DEBUG_DEV('pack: extra data = ', packedData)
        strDict = cPickle.dumps(packedData, -1)
        return packPascalString(strDict)

    @staticmethod
    def __unpackPlayerExtraData(packedData, initialOffset):
        LOG_DEBUG_DEV('unpack: extra data = ', packedData)
        offset = initialOffset
        strDict, lenKeyBytes = unpackPascalString(packedData, offset)
        offset += lenKeyBytes
        return (cPickle.loads(strDict), offset - initialOffset)

    def __packProfileVehicle(self, accountDBID, profileVehicle):
        packed = struct.pack(self._VEHICLE_PROFILE_HEADER, accountDBID, profileVehicle.seasonType, profileVehicle.marksOnGun)
        packed += packPascalString(profileVehicle.vehCompDescr)
        packed += packPascalString(profileVehicle.vehOutfitCD)
        return packed

    def __unpackProfileVehicle(self, packedData):
        accountDBID, seasonType, marksOnGun = struct.unpack_from(self._VEHICLE_PROFILE_HEADER, packedData)
        offset = self._VEHICLE_PROFILE_HEADER_SIZE
        profileVehCD, lenString = unpackPascalString(packedData, offset)
        offset += lenString
        profileOutfitCD, lenString = unpackPascalString(packedData, offset)
        offset += lenString
        self._setProfileVehicle(accountDBID, profileVehCD, profileOutfitCD, seasonType, marksOnGun)
        return offset
