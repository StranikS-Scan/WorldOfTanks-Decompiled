# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/battle_constants.py
from avatar_helpers.aim_global_binding import CTRL_MODE_NAME
from enumerations import Enumeration, AttributeEnumItem

class BATTLE_CTRL_ID(object):
    AMMO, EQUIPMENTS, OPTIONAL_DEVICES, OBSERVED_VEHICLE_STATE, ARENA_LOAD_PROGRESS, ARENA_PERIOD, TEAM_BASES, DEBUG, HIT_DIRECTION, FEEDBACK, CHAT_COMMANDS, MESSAGES, DRR_SCALE, RESPAWN, REPAIR, DYN_SQUADS, AVATAR_PRIVATE_STATS, GAS_ATTACK, FLAG_NOTS, CROSSHAIR, MOD, GUI, MARK1_EVENT_NOTS, MARK1_BONUS = range(1, 25)


REUSABLE_BATTLE_CTRL_IDS = (BATTLE_CTRL_ID.MOD, BATTLE_CTRL_ID.GUI)
BATTLE_CTRL_NAMES = dict([ (v, k) for k, v in BATTLE_CTRL_ID.__dict__.iteritems() if not k.startswith('_') ])

def getBattleCtrlName(ctrlID):
    if ctrlID in BATTLE_CTRL_NAMES:
        return BATTLE_CTRL_NAMES[ctrlID]
    else:
        return 'UNKNOWN_{}'.format(ctrlID)


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
    MAX_SPEED = 131072
    RPM = 262144
    VEHICLE_ENGINE_STATE = 524288
    VEHICLE_MOVEMENT_STATE = 1048576


VEHICLE_DEVICES = ('engine', 'ammoBay', 'gun', 'turretRotator', 'leftTrack', 'rightTrack', 'surveyingDevice', 'radio', 'fuelTank')
WHEEL_VEHICLE_DEVICES = ('engine', 'ammoBay', 'gun', 'turretRotator', 'leftWheel', 'rightWheel', 'surveyingDevice', 'radio', 'fuelTank')
VEHICLE_GUI_ITEMS = ('engine', 'ammoBay', 'gun', 'turretRotator', 'chassis', 'surveyingDevice', 'radio', 'fuelTank')
WHEEL_VEHICLE_GUI_ITEMS = ('engine', 'ammoBay', 'gun', 'turretRotator', 'wheelChassis', 'surveyingDevice', 'radio', 'fuelTank')
VEHICLE_DEVICE_IN_COMPLEX_ITEM = {'leftTrack': 'chassis',
 'rightTrack': 'chassis'}
VEHICLE_COMPLEX_ITEMS = {'chassis': ('leftTrack', 'rightTrack'),
 'wheelChassis': ('leftWheel', 'rightWheel')}
DEVICE_STATES_RANGE = ('normal', 'critical', 'destroyed', 'repaired')
DEVICE_STATE_AS_DAMAGE = ('critical', 'destroyed')

class VEHICLE_INDICATOR_TYPE(object):
    DEFAULT = 'Tank'
    SPG = 'SPG'
    AT_SPG = 'AT-SPG'
    CAR = 'Car'


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
    PLAYER_KILLED_ENEMY, PLAYER_DAMAGED_HP_ENEMY, PLAYER_DAMAGED_DEVICE_ENEMY, PLAYER_SPOTTED_ENEMY, PLAYER_ASSIST_TO_KILL_ENEMY, PLAYER_USED_ARMOR, PLAYER_CAPTURED_BASE, PLAYER_DROPPED_CAPTURE, VEHICLE_HEALTH, VEHICLE_HIT, VEHICLE_ARMOR_PIERCED, VEHICLE_DEAD, VEHICLE_SHOW_MARKER, VEHICLE_ATTRS_CHANGED, VEHICLE_IN_FOCUS, VEHICLE_HAS_AMMO, SHOW_VEHICLE_DAMAGES_DEVICES, HIDE_VEHICLE_DAMAGES_DEVICES, MINIMAP_SHOW_MARKER, MINIMAP_MARK_CELL = range(1, 21)


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


_CTRL_MODE_TO_VIEW_ID = {CTRL_MODE_NAME.ARCADE: CROSSHAIR_VIEW_ID.ARCADE,
 CTRL_MODE_NAME.STRATEGIC: CROSSHAIR_VIEW_ID.STRATEGIC,
 CTRL_MODE_NAME.SNIPER: CROSSHAIR_VIEW_ID.SNIPER,
 CTRL_MODE_NAME.POSTMORTEM: CROSSHAIR_VIEW_ID.POSTMORTEM,
 CTRL_MODE_NAME.FALLOUT_DEATH: CROSSHAIR_VIEW_ID.POSTMORTEM}

def getCrosshairViewIDByCtrlMode(ctrlMode):
    """Gets viewID by avatar control mode.
    If control mode has not UI, that function return CROSSHAIR_VIEW_ID.UNDEFINED
    :param ctrlMode: string containing one of CTRL_MODE_NAME.
    :return: integer containing one of CROSSHAIR_VIEW_ID.
    """
    if ctrlMode in _CTRL_MODE_TO_VIEW_ID:
        viewID = _CTRL_MODE_TO_VIEW_ID[ctrlMode]
    else:
        viewID = CROSSHAIR_VIEW_ID.UNDEFINED
    return viewID


class GUN_RELOADING_VALUE_TYPE(object):
    TIME = 1
    PERCENT = 2


class BATTLE_SYNC_LOCKS(object):
    MARK1_EVENT_NOTIFICATIONS = 1
    BATTLE_MARK1_AT_BASE_SOUND_LOCK = 2
