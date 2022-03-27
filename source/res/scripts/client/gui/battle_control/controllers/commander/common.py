# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/common.py
from collections import namedtuple
import enum
import logging
import BigWorld
import Keys
import Math
import math_utils
from RTSShared import RTSManner
from gui.impl.gen import R
from skeletons.battle_replay import IReplayConvertible
_logger = logging.getLogger(__name__)
_TERRAIN_COLLIDE_SKIP_FLAGS = 119
_TERRAIN_TEST_HEIGHT = 10000.0
_CAM_MIN_SCALE = 1.0
_CAM_MAX_SCALE = 2.0
_CAM_STEP = 50.0
ALLY_INVADERS_RADIUS_EPS = 30

class BaseHighlightType(object):
    ALLY = 'ally'
    ENEMY = 'enemy'
    NEUTRAL = 'neutral'
    VARIANTS = (ALLY, ENEMY, NEUTRAL)


class FocusPriority(IReplayConvertible, enum.Enum):
    NONE = 0
    MARKER = 1
    PANEL = 2
    MAX = 3

    @staticmethod
    def dumpSafe(value):
        return value.value

    @staticmethod
    def loadSafe(value):
        return FocusPriority(value)


class MoveStates(enum.Enum):
    INIT = 0
    PREPARE_MOVE = 1
    WAITING = 2
    START_MOVE = 3
    MOVE = 4
    ORIENT = 5
    FINISH_MOVE = 6
    FINI = 7


_ModifierKey = namedtuple('ModifierKey', ['text', 'key1', 'key2'])

class MappedKeys(object):
    KEY_HALT = 1
    KEY_MOVE_UP = 2
    KEY_MOVE = 3
    KEY_POINT_ORDER = 4
    KEY_POINT_SELECT = 5
    KEY_GROUP_0 = 6
    KEY_GROUP_1 = 7
    KEY_GROUP_2 = 8
    KEY_GROUP_3 = 9
    KEY_GROUP_4 = 10
    KEY_GROUP_5 = 11
    KEY_GROUP_6 = 12
    KEY_GROUP_7 = 13
    KEY_GROUP_8 = 14
    KEY_GROUP_9 = 15
    KEY_CAM_FORWARD = 16
    KEY_CAM_BACK = 17
    KEY_CAM_LEFT = 18
    KEY_CAM_RIGHT = 19
    KEY_ROTATE_LEFT = 20
    KEY_ROTATE_RIGHT = 21
    KEY_GOTO_CONTACT = 22
    KEY_FOCUS_CAMERA = 23
    KEY_ROTATE_CAMERA = 24
    KEY_CONTROL_VEHICLE = 25
    KEY_DEFAULT_CAMERA = 26
    KEY_SHOW_NEXT = 27
    KEY_SHOW_TRAJECTORY = 32
    KEY_SHOW_ORDER_LINE = 33
    KEY_SCOUT_MANNER = 34
    KEY_HOLD_MANNER = 35
    KEY_RETREAT = 36
    KEY_SMART_MANNER = 37
    KEY_FORCE_ORDER_MODE = 38
    KEY_CAM_ZOOM = 39
    KEY_REV_MOVE = 40
    MOD_REVERSE = 41
    MOD_EXPAND_SELECTION = 42
    MOD_TOGGLE_SELECTION = 43
    MOD_CREATE_GROUP = 44
    MOD_APPEND_ORDER = 45
    __keyMap = {KEY_HALT: Keys.KEY_SPACE,
     KEY_MOVE_UP: Keys.KEY_E,
     KEY_SHOW_NEXT: Keys.KEY_R,
     KEY_MOVE: Keys.KEY_M,
     KEY_POINT_ORDER: Keys.KEY_RIGHTMOUSE,
     KEY_POINT_SELECT: Keys.KEY_LEFTMOUSE,
     KEY_GROUP_0: Keys.KEY_0,
     KEY_GROUP_1: Keys.KEY_1,
     KEY_GROUP_2: Keys.KEY_2,
     KEY_GROUP_3: Keys.KEY_3,
     KEY_GROUP_4: Keys.KEY_4,
     KEY_GROUP_5: Keys.KEY_5,
     KEY_GROUP_6: Keys.KEY_6,
     KEY_GROUP_7: Keys.KEY_7,
     KEY_GROUP_8: Keys.KEY_8,
     KEY_GROUP_9: Keys.KEY_9,
     KEY_CAM_FORWARD: Keys.KEY_W,
     KEY_CAM_BACK: Keys.KEY_S,
     KEY_CAM_LEFT: Keys.KEY_A,
     KEY_CAM_RIGHT: Keys.KEY_D,
     KEY_ROTATE_LEFT: Keys.KEY_COMMA,
     KEY_ROTATE_RIGHT: Keys.KEY_PERIOD,
     KEY_GOTO_CONTACT: Keys.KEY_X,
     KEY_FOCUS_CAMERA: Keys.KEY_O,
     KEY_ROTATE_CAMERA: Keys.KEY_MIDDLEMOUSE,
     KEY_CONTROL_VEHICLE: Keys.KEY_Q,
     KEY_DEFAULT_CAMERA: Keys.KEY_HOME,
     KEY_SHOW_TRAJECTORY: Keys.KEY_Z,
     KEY_SHOW_ORDER_LINE: Keys.KEY_LALT,
     KEY_SCOUT_MANNER: Keys.KEY_T,
     KEY_HOLD_MANNER: Keys.KEY_R,
     KEY_SMART_MANNER: Keys.KEY_E,
     KEY_RETREAT: Keys.KEY_F,
     KEY_FORCE_ORDER_MODE: Keys.KEY_C,
     KEY_CAM_ZOOM: Keys.KEY_MIDDLEMOUSE,
     KEY_REV_MOVE: Keys.KEY_F}
    __modifierMap = {MOD_REVERSE: Keys.MODIFIER_ALT,
     MOD_EXPAND_SELECTION: Keys.MODIFIER_SHIFT,
     MOD_TOGGLE_SELECTION: Keys.MODIFIER_CTRL,
     MOD_CREATE_GROUP: Keys.MODIFIER_CTRL,
     MOD_APPEND_ORDER: Keys.MODIFIER_SHIFT}
    __key_by_manner = {RTSManner.DEFENSIVE: KEY_SMART_MANNER,
     RTSManner.SCOUT: KEY_SCOUT_MANNER,
     RTSManner.HOLD: KEY_HOLD_MANNER}
    __modifierKeyInfoMap = {Keys.MODIFIER_SHIFT: _ModifierKey(text=R.strings.readable_key_names.KEY_SHIFT(), key1=Keys.KEY_LSHIFT, key2=Keys.KEY_RSHIFT),
     Keys.MODIFIER_CTRL: _ModifierKey(text=R.strings.readable_key_names.KEY_CTRL(), key1=Keys.KEY_LCONTROL, key2=Keys.KEY_RCONTROL),
     Keys.MODIFIER_ALT: _ModifierKey(text=R.strings.readable_key_names.KEY_ALT(), key1=Keys.KEY_LALT, key2=Keys.KEY_RALT)}

    @classmethod
    def getKey(cls, key):
        return cls.__keyMap.get(key)

    @classmethod
    def isModifierKey(cls, mappedMod):
        return mappedMod in cls.__modifierMap.keys()

    @classmethod
    def isKey(cls, event, mappedKey, checkDown=True):
        return False if checkDown and not event.isKeyDown() else cls.isMappedTo(event.key, mappedKey)

    @classmethod
    def getModifierKeyString(cls, mappedMod):
        mods = cls.__modifierMap.get(mappedMod)
        if mods not in cls.__modifierKeyInfoMap:
            return ''
        modKeyInfo = cls.__modifierKeyInfoMap[mods]
        return modKeyInfo.text

    @classmethod
    def isMappedTo(cls, keyCode, mappedKey):
        return cls.__keyMap.get(mappedKey) == keyCode

    @classmethod
    def isModifierDown(cls, mappedMod):
        mods = cls.__modifierMap.get(mappedMod)
        if mods is None:
            return False
        else:
            mods = cls.__modifierMap.get(mappedMod)
            if mods not in cls.__modifierKeyInfoMap:
                return False
            modKeyInfo = cls.__modifierKeyInfoMap[mods]
            return False if not (BigWorld.isKeyDown(modKeyInfo.key1) or BigWorld.isKeyDown(modKeyInfo.key2)) else True

    @classmethod
    def getKeyCodeByManner(cls, manner):
        return cls.getKey(cls.__key_by_manner.get(manner))

    @classmethod
    def getMannerByKeyCode(cls, keyCode):
        for manner in cls.__key_by_manner.iterkeys():
            if cls.isMappedTo(keyCode, cls.__key_by_manner.get(manner)):
                return manner

        return None


def hasAppendModifiers():
    return any(map(BigWorld.isKeyDown, (Keys.KEY_LCONTROL, Keys.KEY_RCONTROL)))


def getWaterHeight(vector):
    testHeight = 10000.0
    x = vector.x
    z = vector.z
    dist = BigWorld.wg_collideWater(Math.Vector3(x, testHeight, z), Math.Vector3(x, -testHeight, z))
    if dist == -1.0:
        return None
    else:
        if dist > 0.0:
            dist = testHeight - dist
        return dist


def getPointOnTerrain(vector, startY=None, priorityDirection=None):
    player = BigWorld.player()
    if player is None:
        return
    else:
        spaceID = player.spaceID
        x = vector.x
        z = vector.z
        if startY is not None:
            point, _ = _getClosestCollidePointAndDirection(spaceID, x, startY, z, priorityDirection)
            return point
        collideResult = BigWorld.wg_collideSegment(spaceID, Math.Vector3(x, _TERRAIN_TEST_HEIGHT, z), Math.Vector3(x, -_TERRAIN_TEST_HEIGHT, z), _TERRAIN_COLLIDE_SKIP_FLAGS)
        return None if collideResult is None else collideResult.closestPoint


def calculateScaleFactor(vehiclePos, cameraPos):
    return math_utils.clamp(_CAM_MIN_SCALE, _CAM_MAX_SCALE, vehiclePos.distTo(cameraPos) / _CAM_STEP)


def getClosestCollideDirection(x, startY, z):
    player = BigWorld.player()
    if player is None:
        return
    else:
        _, direction = _getClosestCollidePointAndDirection(player.spaceID, x, startY, z)
        return direction


def center(positions):
    result = Math.Vector3(0, 0, 0)
    for position in positions:
        result += Math.Vector3(position)

    if positions:
        result /= len(positions)
    return result


def addModel(model):
    player = BigWorld.player()
    if player is not None:
        player.addModel(model)
    else:
        _logger.debug('Player not found, model is not added')
    return


def delModel(model):
    player = BigWorld.player()
    if player is not None:
        player.delModel(model)
    else:
        _logger.debug('Player not found')
    return


def isShowAlternateUI():
    return BigWorld.isKeyDown(Keys.KEY_LALT) or BigWorld.isKeyDown(Keys.KEY_RALT)


def _getClosestCollidePointAndDirection(spaceID, x, startY, z, priorityDirection=None):
    closestPoint = None
    closestDirection = None
    isPrioritized = priorityDirection is not None
    if not isPrioritized:
        priorityDirection = 1.0
    for direction in (priorityDirection, -priorityDirection):
        collideResult = BigWorld.wg_collideSegment(spaceID, Math.Vector3(x, startY, z), Math.Vector3(x, direction * _TERRAIN_TEST_HEIGHT, z), _TERRAIN_COLLIDE_SKIP_FLAGS)
        if collideResult is None:
            continue
        collidePoint = collideResult.closestPoint
        if collidePoint is None:
            continue
        if isPrioritized:
            return (collidePoint, direction)
        if closestPoint is None or abs(closestPoint.y - startY) >= abs(collidePoint.y - startY):
            closestPoint = collidePoint
            closestDirection = direction

    return (closestPoint, closestDirection)
