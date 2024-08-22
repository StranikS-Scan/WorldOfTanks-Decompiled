# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/common/fun_random_common/fun_constants.py
import constants
import UnitBase
from constants_utils import ConstInjector
DEFAULT_ASSETS_PACK = 'undefined'
DEFAULT_SETTINGS_KEY = 'undefined'
DEFAULT_PRIORITY = 0
FUN_EVENT_ID_KEY = 'funEventID'
UNKNOWN_EVENT_ID = 0
UNKNOWN_EVENT_NAME = 'unknown_event'
UNKNOWN_WWISE_REMAPPING = 'unknownRemapping'
FUN_GAME_PARAMS_KEY = 'fun_random_config'
BATTLE_MODE_VEH_TAGS_EXCEPT_FUN = constants.BATTLE_MODE_VEHICLE_TAGS - {'fun_random'}

class FunSubModeImpl(object):
    DEV_TEST = 0
    DEFAULT = 1
    ALL = (DEFAULT,) + ((DEV_TEST,) if constants.IS_DEVELOPMENT else ())


class FunProgressionCondition(object):
    BATTLES = 'battles'
    TOP = 'top'
    WIN = 'win'
    ALL = (BATTLES, TOP, WIN)


class FunEfficiencyParameter(object):
    KILLS = 'kills'
    SPOTTED = 'spotted'
    STUN = 'damageAssistedStun'
    DAMAGE_DEALT = 'damageDealt'
    DAMAGE_ASSISTED = 'damageAssisted'
    DAMAGE_BLOCKED_BY_ARMOR = 'damageBlockedByArmor'
    CAPTURE_POINTS = 'capturePoints'
    DROPPED_CAPTURE_POINTS = 'droppedCapturePoints'
    ALL = (KILLS,
     SPOTTED,
     STUN,
     DAMAGE_DEALT,
     DAMAGE_ASSISTED,
     DAMAGE_BLOCKED_BY_ARMOR,
     CAPTURE_POINTS,
     DROPPED_CAPTURE_POINTS)


class FunEfficiencyParameterCount(object):
    MIN = 3
    MAX = 5


class ARENA_GUI_TYPE(constants.ARENA_GUI_TYPE, ConstInjector):
    FUN_RANDOM = 29


class UNIT_MGR_FLAGS(UnitBase.UNIT_MGR_FLAGS, ConstInjector):
    FUN_RANDOM = 131072


class ROSTER_TYPE(UnitBase.ROSTER_TYPE, ConstInjector):
    FUN_RANDOM_ROSTER = UNIT_MGR_FLAGS.FUN_RANDOM | UNIT_MGR_FLAGS.SQUAD


class INVITATION_TYPE(constants.INVITATION_TYPE, ConstInjector):
    FUN_RANDOM = constants.PREBATTLE_TYPE.FUN_RANDOM


class CLIENT_UNIT_CMD(UnitBase.CLIENT_UNIT_CMD, ConstInjector):
    CHANGE_FUN_EVENT_ID = 29
