# Embedded file name: scripts/client/gui/prb_control/settings.py
from UnitBase import UNIT_ERROR, UNIT_BROWSER_ERROR
from constants import PREBATTLE_TYPE
from prebattle_shared import SETTING_DEFAULTS, PrebattleSettings
from gui.shared.utils import CONST_CONTAINER, BitmaskHelper
VEHICLE_MIN_LEVEL = 1
VEHICLE_MAX_LEVEL = 10
VEHICLE_DEF_LEVEL_RANGE = (VEHICLE_MIN_LEVEL, VEHICLE_MAX_LEVEL)
TEAM_MAX_LIMIT = 150
INVITE_COMMENT_MAX_LENGTH = 400
UNIT_COMMENT_MAX_LENGTH = 240
CREATOR_SLOT_INDEX = 0
CREATOR_ROSTER_SLOT_INDEXES = (0, 1)
UNIT_CLOSED_SLOTS_MASK = 255 - 0
UNIT_CLOSED_SLOT_COST = 1
AUTO_SEARCH_UNITS_ARG_TIME = 5
UNIT_MIN_RECOMMENDED_LEVEL = 40

class CTRL_ENTITY_TYPE(object):
    UNKNOWN = 0
    PREBATTLE = 1
    UNIT = 2
    PREQUEUE = 3


class FUNCTIONAL_EXIT(object):
    NO_FUNC = 1
    INTRO_PREBATTLE = 2
    PREBATTLE = 3
    INTRO_UNIT = 4
    UNIT = 5
    SWITCH = 6
    SQUAD = 7
    BATTLE_TUTORIAL = 8
    RANDOM = 9
    PREBATTLE_RANGE = (NO_FUNC,
     INTRO_PREBATTLE,
     PREBATTLE,
     BATTLE_TUTORIAL,
     SQUAD,
     SWITCH,
     RANDOM)
    UNIT_RANGE = (NO_FUNC,
     INTRO_UNIT,
     UNIT,
     BATTLE_TUTORIAL,
     SQUAD,
     SWITCH,
     RANDOM)


class FUNCTIONAL_INIT_RESULT(BitmaskHelper):
    UNDEFINED = 0
    INITED = 1
    LOAD_PAGE = 2
    LOAD_WINDOW = 4


class UNIT_MODE_FLAGS(BitmaskHelper):
    UNDEFINED = 0
    SHOW_LIST = 1


IGNORED_UNIT_MGR_ERRORS = (UNIT_ERROR.OK, UNIT_ERROR.REMOVED_PLAYER, UNIT_ERROR.TIMEOUT)
IGNORED_UNIT_BROWSER_ERRORS = (UNIT_BROWSER_ERROR.OK,
 UNIT_BROWSER_ERROR.UNSUBSCRIBED,
 UNIT_BROWSER_ERROR.ACCEPT_TIMEOUT,
 UNIT_BROWSER_ERROR.ACCEPT_CANCELED,
 UNIT_BROWSER_ERROR.SEARCH_CANCELED)
UNIT_ERRORS_TRANSLATE_AS_WARNINGS = (UNIT_ERROR.KICKED_PLAYER,
 UNIT_ERROR.KICKED_CANDIDATE,
 UNIT_ERROR.UNIT_ASSEMBLER_TIMEOUT,
 UNIT_ERROR.INVITE_REMOVED,
 UNIT_ERROR.INVITE_REMOVED,
 UNIT_ERROR.ALREADY_INVITED,
 UNIT_ERROR.WAITING_FOR_JOIN,
 UNIT_ERROR.CLAN_CHANGED,
 UNIT_ERROR.CANT_PICK_LEADER,
 UNIT_ERROR.NO_CLAN_MEMBERS)
RETURN_INTRO_UNIT_MGR_ERRORS = (UNIT_ERROR.KICKED_CANDIDATE, UNIT_ERROR.KICKED_PLAYER)
UNIT_ERROR_NAMES = dict([ (v, k) for k, v in UNIT_ERROR.__dict__.iteritems() ])
UNIT_BROWSER_ERROR_NAMES = dict([ (v, k) for k, v in UNIT_BROWSER_ERROR.__dict__.iteritems() ])

class UNIT_NOTIFICATION_KEY(object):
    PLAYER_OFFLINE = 'playerOffline'
    PLAYER_ONLINE = 'playerOnline'
    PLAYER_ADDED = 'playerAdded'
    PLAYER_REMOVED = 'playerRemoved'
    GIVE_LEADERSHIP = 'giveLeadership'


class PREBATTLE_ACTION_NAME(object):
    UNDEFINED = ''
    JOIN_RANDOM_QUEUE = 'joinRandomQueue'
    LEAVE_RANDOM_QUEUE = 'leaveRandomQueue'
    JOIN_EVENT_BATTLES_QUEUE = 'joinEventBattlesQueue'
    LEAVE_EVENT_BATTLES_QUEUE = 'leaveEventBattlesQueue'
    TRAINING = 'trainingList'
    LEAVE_TRAINING_LIST = 'leaveTrainingList'
    COMPANY = 'companyList'
    SPEC_BATTLE = 'specBattleList'
    PREBATTLE_LEAVE = 'prebattleLeave'
    PREQUEUE_LEAVE = 'prequeueLeave'
    SQUAD = 'squad'
    TOURNAMENT = 'tournament'
    CLAN = 'clan'
    UNIT = 'unit'
    UNIT_LEAVE = 'unitLeave'
    HISTORICAL = 'historical'
    LEAVE_HISTORICAL = 'leaveHistorical'
    FORT = 'sortie'
    FORT_LEAVE = 'fortLeave'
    BATTLE_TUTORIAL = 'tutorial'


class PREBATTLE_INIT_STEP:
    SETTING_RECEIVED = 1
    ROSTERS_RECEIVED = 2
    INITED = SETTING_RECEIVED | ROSTERS_RECEIVED


class SELECTOR_BATTLE_TYPES:
    UNIT = 'unit'
    HISTORICAL = 'historical'
    SORTIE = 'sortie'


class REQUEST_TYPE(object):
    CREATE, ASSIGN, JOIN, LEAVE, SET_TEAM_STATE, SET_PLAYER_STATE, SWAP_TEAMS, CHANGE_SETTINGS, CHANGE_OPENED, CHANGE_COMMENT, CHANGE_DIVISION, CHANGE_ARENA_VOIP, KICK, SEND_INVITE, PREBATTLES_LIST, LOCK, CLOSE_SLOT, SET_VEHICLE, SET_ROSTERS_SLOTS, AUTO_SEARCH, ACCEPT_SEARCH, DECLINE_SEARCH, BATTLE_QUEUE, CHANGE_UNIT_STATE, UNITS_LIST, UNITS_RECENTER, UNITS_REFRESH, UNITS_NAV_LEFT, UNITS_NAV_RIGHT, CHANGE_USER_STATUS, GIVE_LEADERSHIP, GET_ROSTER = range(1, 33)


REQUEST_TYPE_NAMES = dict([ (v, k) for k, v in REQUEST_TYPE.__dict__.iteritems() ])

class PREQUEUE_SETTING_NAME(CONST_CONTAINER):
    BATTLE_ID = 'battleID'
    SELECTED_VEHICLE_ID = 'selectedVehicleID'
    PRICE_INDEX = 'priceIndex'


class PREBATTLE_SETTING_NAME(object):
    CREATOR = 'creator'
    IS_OPENED = 'isOpened'
    COMMENT = 'comment'
    ARENA_TYPE_ID = 'arenaTypeID'
    ROUND_LENGTH = 'roundLength'
    ARENA_VOIP_CHANNELS = 'arenaVoipChannels'
    CURRENT_USER_STATUS = 'currentUserStatus'
    DEFAULT_ROSTER = 'defaultRoster'
    VEHICLE_LOCK_MODE = 'vehicleLockMode'
    DIVISION = 'division'
    START_TIME = 'startTime'
    BATTLES_LIMIT = 'battlesLimit'
    WINS_LIMIT = 'winsLimit'
    EXTRA_DATA = 'extraData'
    LIMITS = 'limits'
    DESTROY_IF_CREATOR_OUT = 'destroyIfCreatorOut'


class PREBATTLE_RESTRICTION:
    LIMIT_MIN_COUNT = 'limit/minCount'
    LIMIT_MAX_COUNT = 'limit/maxCount'
    LIMIT_LEVEL = 'limits/level'
    LIMIT_TOTAL_LEVEL = 'limit/totalLevel'
    LIMIT_CLASSES = 'limits/classes'
    LIMIT_CLASS_LEVEL = 'limits/classLevel'
    LIMIT_VEHICLES = 'limits/vehicles'
    LIMIT_NATIONS = 'limits/nations'
    LIMIT_COMPONENTS = 'limits/components'
    LIMIT_AMMO = 'limits/ammo'
    LIMIT_SHELLS = 'limits/shells'
    LIMIT_LIGHT_TANK = 'limits/classes/lightTank'
    LIMIT_MEDIUM_TANK = 'limits/classes/mediumTank'
    LIMIT_HEAVY_TANK = 'limits/classes/heavyTank'
    LIMIT_SPG = 'limits/classes/SPG'
    LIMIT_AT_SPG = 'limits/classes/AT-SPG'
    HAS_PLAYER_IN_BATTLE = 'player/inBattle'
    VEHICLE_NOT_READY = 'vehicle/notReady'
    VEHICLE_NOT_PRESENT = 'vehicle/notPresent'
    VEHICLE_IN_BATTLE = 'vehicle/inBattle'
    VEHICLE_BROKEN = 'vehicle/broken'
    VEHICLE_ROAMING = 'vehicle/roaming'
    VEHICLE_RENTALS_IS_OVER = 'vehicle/rentalsIsOver'
    VEHICLE_IGR_RENTALS_IS_OVER = 'vehicle/igrRentalsIsOver'
    VEHICLE_IN_PREMIUM_IGR_ONLY = 'vehicle/inPremiumIgrOnly'
    VEHICLE_NOT_SUPPORTED = 'vehicle/not_supported'
    CREW_NOT_FULL = 'crew/notFull'
    SERVER_LIMITS = (LIMIT_MIN_COUNT,
     LIMIT_MAX_COUNT,
     LIMIT_LEVEL,
     LIMIT_TOTAL_LEVEL,
     LIMIT_CLASSES,
     LIMIT_CLASS_LEVEL,
     LIMIT_VEHICLES,
     LIMIT_NATIONS,
     LIMIT_COMPONENTS,
     LIMIT_AMMO,
     LIMIT_SHELLS)
    VEHICLE_CLASS_LIMITS = (('lightTank', LIMIT_LIGHT_TANK),
     ('mediumTank', LIMIT_MEDIUM_TANK),
     ('heavyTank', LIMIT_HEAVY_TANK),
     ('SPG', LIMIT_SPG),
     ('AT-SPG', LIMIT_AT_SPG))
    VEHICLE_INVALID_STATES = (VEHICLE_NOT_READY,
     VEHICLE_NOT_PRESENT,
     VEHICLE_IN_BATTLE,
     VEHICLE_BROKEN,
     VEHICLE_ROAMING,
     VEHICLE_RENTALS_IS_OVER)

    @classmethod
    def getVehClassRestrictions(cls):
        return dict(((restriction, tag) for tag, restriction in cls.VEHICLE_CLASS_LIMITS))

    @classmethod
    def getVehClassTags(cls):
        return dict(((tag, restriction) for tag, restriction in cls.VEHICLE_CLASS_LIMITS))

    @classmethod
    def inVehClassLimit(cls, search):
        for tag, restriction in cls.VEHICLE_CLASS_LIMITS:
            if restriction == search:
                return True

        return False


class UNIT_RESTRICTION(object):
    UNDEFINED = ''
    NOT_READY_IN_SLOTS = 'slots/notReadyPlayers'
    MIN_SLOTS = 'slots/minOccupiedSlots'
    ZERO_TOTAL_LEVEL = 'roster/zeroTotalLevel'
    MIN_TOTAL_LEVEL = 'roster/minTotalLevel'
    MAX_TOTAL_LEVEL = 'roster/maxTotalLevel'
    INVALID_TOTAL_LEVEL = 'roster/invalidTotalLevel'
    NEED_PLAYERS_SEARCH = 'roster/needPlayersSearch'
    IS_IN_IDLE = 'state/isInIdle'
    IS_IN_ARENA = 'state/isInArena'
    UNIT_IS_FULL = 'state/full'
    UNIT_IS_LOCKED = 'state/locked'
    VEHICLE_NOT_SELECTED = 'vehicle/notSelected'
    VEHICLE_NOT_VALID = 'vehicle/notValid'
    VEHICLE_NOT_FOUND = 'vehicle/notFound'


class PREBATTLE_ROSTER(object):
    UNKNOWN = -1
    ASSIGNED = 0
    UNASSIGNED = 16
    ASSIGNED_IN_TEAM1 = ASSIGNED | 1
    UNASSIGNED_IN_TEAM1 = UNASSIGNED | 1
    ASSIGNED_IN_TEAM2 = ASSIGNED | 2
    UNASSIGNED_IN_TEAM2 = UNASSIGNED | 2
    ALL = (ASSIGNED_IN_TEAM1,
     UNASSIGNED_IN_TEAM1,
     ASSIGNED_IN_TEAM2,
     UNASSIGNED_IN_TEAM2)
    PREBATTLE_RANGES = {PREBATTLE_TYPE.TRAINING: ALL,
     PREBATTLE_TYPE.SQUAD: (ASSIGNED_IN_TEAM1,),
     PREBATTLE_TYPE.COMPANY: (ASSIGNED_IN_TEAM1, UNASSIGNED_IN_TEAM1),
     PREBATTLE_TYPE.TOURNAMENT: ALL,
     PREBATTLE_TYPE.CLAN: ALL}

    @classmethod
    def getRange(cls, pbType, team = None):
        result = ()
        if pbType in cls.PREBATTLE_RANGES:
            result = cls.PREBATTLE_RANGES[pbType]
            if team is not None:
                result = filter(lambda r: r & team, result)
        return result


_PREBATTLE_DEFAULT_SETTINGS = SETTING_DEFAULTS
_PREBATTLE_DEFAULT_SETTINGS.update({'limits': {0: {},
            1: {},
            2: {}}})

def makePrebattleSettings(settings = None):
    if not settings:
        settings = _PREBATTLE_DEFAULT_SETTINGS
    return PrebattleSettings(settings)


class QUEUE_EVENT_TYPE(object):
    ENQUEUED = 1
    DEQUEUED = 2
    ENQUEUE_ERROR = 3
    KICKED_FROM_QUEUE = 4
    KICKED_FROM_ARENA = 5


class FUNCTIONAL_ORDER(object):
    ENTRY = (CTRL_ENTITY_TYPE.PREQUEUE, CTRL_ENTITY_TYPE.PREBATTLE, CTRL_ENTITY_TYPE.UNIT)
    ACTION = (CTRL_ENTITY_TYPE.UNIT, CTRL_ENTITY_TYPE.PREQUEUE, CTRL_ENTITY_TYPE.PREBATTLE)
    EXIT_FROM_QUEUE = (CTRL_ENTITY_TYPE.PREBATTLE, CTRL_ENTITY_TYPE.PREQUEUE)
    BEFORE_GENERAL_CHECKING = (CTRL_ENTITY_TYPE.PREQUEUE,)
    AFTER_GENERAL_CHECKING = (CTRL_ENTITY_TYPE.UNIT, CTRL_ENTITY_TYPE.PREBATTLE)
