# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/aih_constants.py


class ShakeReason(object):
    OWN_SHOT = 0
    OWN_SHOT_DELAYED = 1
    HIT = 2
    HIT_NO_DAMAGE = 3
    SPLASH = 4


class CTRL_MODE_NAME(object):
    ARCADE = 'arcade'
    STRATEGIC = 'strategic'
    ARTY = 'arty'
    SNIPER = 'sniper'
    POSTMORTEM = 'postmortem'
    DEBUG = 'debug'
    CAT = 'cat'
    VIDEO = 'video'
    MAP_CASE = 'mapcase'
    MAP_CASE_ARCADE = 'arcadeMapcase'
    MAP_CASE_ARCADE_EPIC_MINEFIELD = 'arcadeEpicMinefieldMapcase'
    MAP_CASE_EPIC = 'epicMapcase'
    RESPAWN_DEATH = 'respawn'
    DEATH_FREE_CAM = 'deathfreecam'
    DUAL_GUN = 'dualgun'
    VEHICLES_SELECTION = 'vehiclesSelection'
    DEFAULT = ARCADE


CTRL_MODES = (CTRL_MODE_NAME.ARCADE,
 CTRL_MODE_NAME.STRATEGIC,
 CTRL_MODE_NAME.ARTY,
 CTRL_MODE_NAME.SNIPER,
 CTRL_MODE_NAME.POSTMORTEM,
 CTRL_MODE_NAME.DEBUG,
 CTRL_MODE_NAME.CAT,
 CTRL_MODE_NAME.VIDEO,
 CTRL_MODE_NAME.MAP_CASE,
 CTRL_MODE_NAME.MAP_CASE_ARCADE,
 CTRL_MODE_NAME.MAP_CASE_EPIC,
 CTRL_MODE_NAME.RESPAWN_DEATH,
 CTRL_MODE_NAME.DEATH_FREE_CAM,
 CTRL_MODE_NAME.DUAL_GUN,
 CTRL_MODE_NAME.MAP_CASE_ARCADE_EPIC_MINEFIELD,
 CTRL_MODE_NAME.VEHICLES_SELECTION)
GUN_MARKER_MIN_SIZE = 32.0
SPG_GUN_MARKER_ELEMENTS_COUNT = 37
SPG_GUN_MARKER_ELEMENTS_RATE = 10
SPG_GUN_MARKER_MIN_SIZE = 50.0
SPG_GUN_MARKER_MAX_SIZE = 100.0
SPG_GUN_MARKER_SCALE_RATE = 10.0

class GUN_MARKER_TYPE(int):
    UNDEFINED = 0
    CLIENT = 1
    SERVER = 2


class GUN_MARKER_FLAG(int):
    UNDEFINED = 0
    CONTROL_ENABLED = 1
    CLIENT_MODE_ENABLED = 2
    SERVER_MODE_ENABLED = 4
    VIDEO_MODE_ENABLED = 8
    ARTY_HIT_ENABLED = 16


class SHOT_RESULT(int):
    UNDEFINED = 0
    NOT_PIERCED = 1
    LITTLE_PIERCED = 2
    GREAT_PIERCED = 3


class STRATEGIC_CAMERA(int):
    AERIAL = 0
    TRAJECTORY = 1
    DEFAULT = AERIAL


class CHARGE_MARKER_STATE(int):
    DIMMED = 0
    LEFT_ACTIVE = 1
    RIGHT_ACTIVE = 2
    VISIBLE = 3
    DEFAULT = DIMMED


MAP_CASE_MODES = (CTRL_MODE_NAME.MAP_CASE_ARCADE_EPIC_MINEFIELD,
 CTRL_MODE_NAME.MAP_CASE,
 CTRL_MODE_NAME.MAP_CASE_ARCADE,
 CTRL_MODE_NAME.MAP_CASE_EPIC,
 CTRL_MODE_NAME.MAP_CASE_ARCADE_EPIC_MINEFIELD)
