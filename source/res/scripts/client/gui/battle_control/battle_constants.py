# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/battle_constants.py
from enumerations import Enumeration, AttributeEnumItem
from shared_utils import CONST_CONTAINER
from constants import SECTOR_STATE

class BATTLE_CTRL_ID(object):
    AMMO, EQUIPMENTS, OPTIONAL_DEVICES, OBSERVED_VEHICLE_STATE, ARENA_LOAD_PROGRESS, ARENA_PERIOD, TEAM_BASES, DEBUG, HIT_DIRECTION, FEEDBACK, CHAT_COMMANDS, MESSAGES, DRR_SCALE, RESPAWN, REPAIR, DYN_SQUADS, AVATAR_PRIVATE_STATS, FLAG_NOTS, CROSSHAIR, MOD, GUI, PERSONAL_EFFICIENCY, TMP_IGNORE_LIST_CTRL, VIEW_POINTS, BATTLE_FIELD_CTRL, PLAYER_GAME_MODE_DATA, TEAM_HEALTH_BAR, ARENA_BORDER, PROGRESS_TIMER, MAPS, SPECTATOR, GAME_NOTIFICATIONS, EPIC_MISSIONS, GAME_MESSAGES_PANEL, QUEST_PROGRESS = range(1, 36)


REUSABLE_BATTLE_CTRL_IDS = (BATTLE_CTRL_ID.MOD, BATTLE_CTRL_ID.GUI)
BATTLE_CTRL_NAMES = dict([ (v, k) for k, v in BATTLE_CTRL_ID.__dict__.iteritems() if not k.startswith('_') ])

def getBattleCtrlName(ctrlID):
    return BATTLE_CTRL_NAMES[ctrlID] if ctrlID in BATTLE_CTRL_NAMES else 'UNKNOWN_{}'.format(ctrlID)


class VIEW_COMPONENT_RULE(object):
    NONE = 0
    PROXY = 1


PLAYERS_PANEL_LENGTH = 24
HIT_INDICATOR_MAX_ON_SCREEN = 5

class SHELL_SET_RESULT(object):
    UNDEFINED = 0
    ADDED = 1
    UPDATED = 2
    CURRENT = 4
    CASSETTE_RELOAD = 8


class CANT_SHOOT_ERROR(object):
    UNDEFINED = ''
    WAITING = 'waiting'
    NO_AMMO = 'no_ammo'
    RELOADING = 'gun_reload'
    EMPTY_CLIP = 'empty_clip'


SHELL_QUANTITY_UNKNOWN = -1

class VEHICLE_VIEW_STATE(object):
    FIRE = 1
    DEVICES = 2
    HEALTH = 4
    DESTROYED = 8
    CREW_DEACTIVATED = 16
    AUTO_ROTATION = 32
    SPEED = 64
    CRUISE_MODE = 128
    REPAIRING = 256
    PLAYER_INFO = 512
    DESTROY_TIMER = 1024
    OBSERVED_BY_ENEMY = 4096
    RESPAWNING = 8192
    SWITCHING = 16384
    DEATHZONE_TIMER = 32768
    DEATH_INFO = 131072
    VEHICLE_CHANGED = 262144
    SIEGE_MODE = 524288
    STUN = 16777216
    CAPTURE_BLOCKED = 33554432
    SMOKE = 67108864
    INSPIRE = 134217728
    UNDER_FIRE = 268435456
    RECOVERY = 536870912
    PROGRESS_CIRCLE = 1073741824
    CLIENT_ONLY = (AUTO_ROTATION, CRUISE_MODE)


VEHICLE_DEVICES = ('engine', 'ammoBay', 'gun', 'turretRotator', 'leftTrack', 'rightTrack', 'surveyingDevice', 'radio', 'fuelTank')
VEHICLE_GUI_ITEMS = ('engine', 'ammoBay', 'gun', 'turretRotator', 'chassis', 'surveyingDevice', 'radio', 'fuelTank')
VEHICLE_DEVICE_IN_COMPLEX_ITEM = {'leftTrack': 'chassis',
 'rightTrack': 'chassis'}
VEHICLE_COMPLEX_ITEMS = {'chassis': ('leftTrack', 'rightTrack')}
DEVICE_STATE_NORMAL = 'normal'
DEVICE_STATE_CRITICAL = 'critical'
DEVICE_STATE_DESTROYED = 'destroyed'
DEVICE_STATES_RANGE = (DEVICE_STATE_NORMAL, DEVICE_STATE_CRITICAL, DEVICE_STATE_DESTROYED)
DEVICE_STATE_AS_DAMAGE = (DEVICE_STATE_CRITICAL, DEVICE_STATE_DESTROYED)

class VEHICLE_INDICATOR_TYPE(object):
    DEFAULT = 'Tank'
    SPG = 'SPG'
    AT_SPG = 'AT-SPG'


EXTRA_SUFFIX = 'Health'
EXTRA_PREFIX_LENGTH = len(EXTRA_SUFFIX)

def makeExtraName(entityName):
    return ''.join([entityName, EXTRA_SUFFIX])


PLAYER_GUI_PROPS = Enumeration('Gui properties for entity', [('ally', {'isFriend': True,
   'base': 'ally'}),
 ('teamKiller', {'isFriend': True,
   'base': 'ally'}),
 ('squadman', {'isFriend': True,
   'base': 'ally'}),
 ('enemy', {'isFriend': False,
   'base': 'enemy'})], instance=AttributeEnumItem)
VEHICLE_WAINING_INTERVAL = 0.05
VEHICLE_UPDATE_INTERVAL = 0.03

class FEEDBACK_EVENT_ID(object):
    PLAYER_KILLED_ENEMY, PLAYER_DAMAGED_HP_ENEMY, PLAYER_DAMAGED_DEVICE_ENEMY, PLAYER_SPOTTED_ENEMY, PLAYER_ASSIST_TO_KILL_ENEMY, PLAYER_ASSIST_TO_STUN_ENEMY, PLAYER_USED_ARMOR, PLAYER_CAPTURED_BASE, PLAYER_DROPPED_CAPTURE, PLAYER_BLOCKED_CAPTURE, VEHICLE_HEALTH, VEHICLE_HIT, VEHICLE_CRITICAL_HIT, VEHICLE_CRITICAL_HIT_DAMAGE, VEHICLE_CRITICAL_HIT_CHASSIS, VEHICLE_CRITICAL_HIT_CHASSIS_PIERCED, VEHICLE_RICOCHET, VEHICLE_ARMOR_PIERCED, VEHICLE_DEAD, VEHICLE_SHOW_MARKER, VEHICLE_ATTRS_CHANGED, VEHICLE_IN_FOCUS, VEHICLE_HAS_AMMO, SHOW_VEHICLE_DAMAGES_DEVICES, HIDE_VEHICLE_DAMAGES_DEVICES, MINIMAP_SHOW_MARKER, MINIMAP_MARK_CELL, DAMAGE_LOG_SUMMARY, POSTMORTEM_SUMMARY, ENEMY_DAMAGED_HP_PLAYER, ENEMY_DAMAGED_DEVICE_PLAYER, VEHICLE_VISIBILITY_CHANGED, VEHICLE_STUN, VEHICLE_INSPIRE, VEHICLE_PASSIVE_ENGINEERING, MINIMAP_MARK_POSITION, MINIMAP_MARK_OBJECTIVE, MINIMAP_MARK_BASE, ENEMY_SECTOR_CAPTURED, DESTRUCTIBLE_DAMAGED, DESTRUCTIBLE_DESTROYED, DESTRUCTIBLES_DEFENDED, DEFENDER_BONUS, SMOKE_ASSIST, INSPIRE_ASSIST, VEHICLE_RECOVERY_STATE_UPDATE, VEHICLE_RECOVERY_CANCELED = range(1, 48)


MARKER_HIT_STATE = {FEEDBACK_EVENT_ID.VEHICLE_HIT: ('hit', 'hit_blocked', '#ingame_gui:hitMarker/blocked'),
 FEEDBACK_EVENT_ID.VEHICLE_CRITICAL_HIT: ('hit_critical', 'hit_critical', '#ingame_gui:hitMarker/critical'),
 FEEDBACK_EVENT_ID.VEHICLE_CRITICAL_HIT_DAMAGE: ('hit_critical', 'hit_critical_damage', ''),
 FEEDBACK_EVENT_ID.VEHICLE_CRITICAL_HIT_CHASSIS: ('hit_critical', 'hit_critical_chassis', '#ingame_gui:hitMarker/critical'),
 FEEDBACK_EVENT_ID.VEHICLE_CRITICAL_HIT_CHASSIS_PIERCED: ('hit_pierced', 'hit_critical_chassis', '#ingame_gui:hitMarker/critical'),
 FEEDBACK_EVENT_ID.VEHICLE_RICOCHET: ('hit', 'hit_ricochet', '#ingame_gui:hitMarker/ricochet'),
 FEEDBACK_EVENT_ID.VEHICLE_ARMOR_PIERCED: ('hit_pierced', '', '')}

class COUNTDOWN_STATE(object):
    UNDEFINED = 0
    WAIT = 1
    START = 2
    STOP = 3
    VISIBLE = (WAIT, START)


class MULTIPLE_TEAMS_TYPE(object):
    UNDEFINED = ''
    FFA = 'ffa'
    TDM = 'teams'
    MIXED = 'mixed'


NEUTRAL_TEAM = 0

class WinStatus(object):
    DRAW = 0
    WIN = 1
    LOSE = 2

    def __init__(self, status):
        self._status = status

    def isValid(self):
        return self._status is not None

    def isWin(self):
        return self._status == self.WIN

    def isLose(self):
        return self._status == self.LOSE

    def isDraw(self):
        return self._status == self.DRAW

    def getStatus(self):
        return self._status

    @classmethod
    def fromWinnerTeam(cls, winnerTeam, isAlly):
        if winnerTeam == 0:
            status = cls.DRAW
        elif isAlly:
            status = cls.WIN
        else:
            status = cls.LOSE
        return cls(status=status)

    @classmethod
    def empty(cls):
        return cls(status=None)


class VEHICLE_LOCATION(object):
    UNDEFINED = 0
    AOI = 1
    FAR = 2
    AOI_TO_FAR = 3


class GAS_ATTACK_STATE(object):
    NO_ATTACK = 0
    PREPEARING = 1
    INSIDE_SAFE_ZONE = 2
    NEAR_SAFE = 3
    NEAR_CLOUD = 4
    INSIDE_CLOUD = 5
    DEAD = 6
    VISIBLE = (NEAR_SAFE, NEAR_CLOUD, INSIDE_CLOUD)


class REPAIR_STATE_ID(object):
    UNRESOLVED = 0
    DISABLED = 1
    READY = 2
    REPAIRING = 3
    COOLDOWN = 4


class CROSSHAIR_VIEW_ID(object):
    UNDEFINED = 0
    ARCADE = 1
    SNIPER = 2
    STRATEGIC = 3
    POSTMORTEM = 4


class PROGRESS_CIRCLE_TYPE(object):
    RESUPPLY_CIRCLE = 1
    SECTOR_BASE_CIRCLE = 2


SECTOR_STATE_ID = {SECTOR_STATE.CLOSED: 0,
 SECTOR_STATE.OPEN: 1,
 SECTOR_STATE.TRANSITION: 2,
 SECTOR_STATE.CAPTURED: 3,
 SECTOR_STATE.BOMBING: 4}

class AUTO_ROTATION_FLAG(int):
    IGNORE_IN_UI = 1
    TURN_ON = 2
    TURN_OFF = 3


class HIT_FLAGS(CONST_CONTAINER):
    HP_DAMAGE = 1
    IS_ALLAY = 2
    IS_BLOCKED = 4
    IS_CRITICAL = 8
    IS_HIGH_EXPLOSIVE = 16
    IS_BATTLE_CONSUMABLES = 32
    IS_NON_PLAYER_ATTACK_REASON = 64


class PERSONAL_EFFICIENCY_TYPE(CONST_CONTAINER):
    DAMAGE = 1
    ASSIST_DAMAGE = 2
    BLOCKED_DAMAGE = 4
    RECEIVED_DAMAGE = 8
    RECEIVED_CRITICAL_HITS = 16
    STUN = 32


class CACHE_RECORDS_IDS(CONST_CONTAINER):
    TMP_IGNORED = 0


class NET_TYPE_OVERRIDE(CONST_CONTAINER):
    DISABLED = -1
    SIEGE_MODE = 5


class STRATEGIC_CAMERA_ID(object):
    UNDEFINED = 0
    AERIAL = 1
    TRAJECTORY = 2


class DestroyTimerViewState(object):
    __slots__ = ('code', 'totalTime', 'level', 'startTime')

    def __init__(self, code, totalTime, level, startTime=None):
        self.code = code
        self.totalTime = totalTime
        self.level = level
        self.startTime = startTime

    def needToShow(self):
        return self.code is not None and self.level is not None

    def needToCloseTimer(self):
        return self.code is not None and self.level is None

    def needToCloseAll(self):
        return self.code is None

    @classmethod
    def makeCloseTimerState(cls, code):
        return cls(code, 0, None)

    @classmethod
    def makeCloseAllState(cls):
        return cls.makeCloseTimerState(code=None)


class DeathZoneTimerViewState(object):
    __slots__ = ('zoneID', 'totalTime', 'level', 'finishTime', 'entered')

    def __init__(self, zoneID, totalTime, level, finishTime, entered=None):
        self.zoneID = zoneID
        self.totalTime = totalTime
        self.level = level
        self.finishTime = finishTime
        self.entered = entered

    def needToShow(self):
        return self.zoneID is not None and self.level is not None

    def needToCloseTimer(self):
        return self.zoneID is not None and self.level is None

    def needToCloseAll(self):
        return self.zoneID is None

    @classmethod
    def makeCloseTimerState(cls, zoneID):
        return cls(zoneID, 0, None, 0)

    @classmethod
    def makeCloseAllState(cls):
        return cls.makeCloseTimerState(zoneID=None)
