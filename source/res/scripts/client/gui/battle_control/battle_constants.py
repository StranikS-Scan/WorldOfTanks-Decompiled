# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/battle_constants.py
from enumerations import Enumeration, AttributeEnumItem
from shared_utils import CONST_CONTAINER

class BATTLE_CTRL_ID(object):
    AMMO, EQUIPMENTS, OPTIONAL_DEVICES, OBSERVED_VEHICLE_STATE, ARENA_LOAD_PROGRESS, ARENA_PERIOD, TEAM_BASES, DEBUG, HIT_DIRECTION, FEEDBACK, CHAT_COMMANDS, MESSAGES, DRR_SCALE, RESPAWN, REPAIR, DYN_SQUADS, AVATAR_PRIVATE_STATS, FLAG_NOTS, CROSSHAIR, MOD, GUI, PERSONAL_EFFICIENCY, TMP_IGNORE_LIST_CTRL, VIEW_POINTS, BATTLE_FIELD_CTRL, PLAYER_GAME_MODE_DATA, TEAM_HEALTH_BAR, GAME_MESSAGES_PANEL, ARENA_BORDER = range(1, 30)


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
    SHOW_DESTROY_TIMER = 1024
    HIDE_DESTROY_TIMER = 2048
    OBSERVED_BY_ENEMY = 4096
    RESPAWNING = 8192
    SWITCHING = 16384
    SHOW_DEATHZONE_TIMER = 32768
    HIDE_DEATHZONE_TIMER = 65536
    DEATH_INFO = 131072
    VEHICLE_CHANGED = 262144
    SIEGE_MODE = 524288
    STUN = 16777216


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
    PLAYER_KILLED_ENEMY, PLAYER_DAMAGED_HP_ENEMY, PLAYER_DAMAGED_DEVICE_ENEMY, PLAYER_SPOTTED_ENEMY, PLAYER_ASSIST_TO_KILL_ENEMY, PLAYER_ASSIST_TO_STUN_ENEMY, PLAYER_USED_ARMOR, PLAYER_CAPTURED_BASE, PLAYER_DROPPED_CAPTURE, VEHICLE_HEALTH, VEHICLE_HIT, VEHICLE_CRITICAL_HIT, VEHICLE_CRITICAL_HIT_DAMAGE, VEHICLE_CRITICAL_HIT_CHASSIS, VEHICLE_RICOCHET, VEHICLE_ARMOR_PIERCED, VEHICLE_DEAD, VEHICLE_SHOW_MARKER, VEHICLE_ATTRS_CHANGED, VEHICLE_IN_FOCUS, VEHICLE_HAS_AMMO, SHOW_VEHICLE_DAMAGES_DEVICES, HIDE_VEHICLE_DAMAGES_DEVICES, MINIMAP_SHOW_MARKER, MINIMAP_MARK_CELL, DAMAGE_LOG_SUMMARY, POSTMORTEM_SUMMARY, ENEMY_DAMAGED_HP_PLAYER, ENEMY_DAMAGED_DEVICE_PLAYER, VEHICLE_VISIBILITY_CHANGED, VEHICLE_STUN = range(1, 32)


MARKER_HIT_STATE = {FEEDBACK_EVENT_ID.VEHICLE_HIT: ('hit_blocked', '#ingame_gui:hitMarker/blocked'),
 FEEDBACK_EVENT_ID.VEHICLE_CRITICAL_HIT: ('hit_critical', '#ingame_gui:hitMarker/critical'),
 FEEDBACK_EVENT_ID.VEHICLE_CRITICAL_HIT_DAMAGE: ('hit_critical_damage', ''),
 FEEDBACK_EVENT_ID.VEHICLE_CRITICAL_HIT_CHASSIS: ('hit_critical_chassis', '#ingame_gui:hitMarker/critical'),
 FEEDBACK_EVENT_ID.VEHICLE_RICOCHET: ('hit_ricochet', '#ingame_gui:hitMarker/ricochet'),
 FEEDBACK_EVENT_ID.VEHICLE_ARMOR_PIERCED: ('hit_pierced', '')}

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


class GUN_RELOADING_VALUE_TYPE(object):
    TIME = 1
    PERCENT = 2


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
