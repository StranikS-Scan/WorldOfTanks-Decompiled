# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/common/comp7_common/comp7_constants.py
import enum
import UnitBase
import constants
from constants_utils import ConstInjector
DEFAULT_ASSETS_PACK = 'undefined'
DEFAULT_SETTINGS_KEY = 'undefined'
DEFAULT_PRIORITY = 0
UNKNOWN_EVENT_ID = 0
UNKNOWN_EVENT_NAME = 'unknown_event'
UNKNOWN_WWISE_REMAPPING = 'unknownRemapping'

class Configs(enum.Enum):
    COMP7_CONFIG = 'comp7_config'
    COMP7_RANKS_CONFIG = 'comp7_ranks_config'
    COMP7_REWARDS_CONFIG = 'comp7_rewards_config'


COMP7_INBATTLE_CONFIGS = (Configs.COMP7_CONFIG.value, Configs.COMP7_RANKS_CONFIG.value)
BATTLE_MODE_VEH_TAGS_EXCEPT_COMP7 = constants.BATTLE_MODE_VEHICLE_TAGS - {'comp7'}

class ARENA_GUI_TYPE(constants.ARENA_GUI_TYPE, ConstInjector):
    COMP7 = 30
    TOURNAMENT_COMP7 = 33
    TRAINING_COMP7 = 34
    COMP7_RANGE = (COMP7, TOURNAMENT_COMP7, TRAINING_COMP7)


class UNIT_MGR_FLAGS(UnitBase.UNIT_MGR_FLAGS, ConstInjector):
    COMP7 = 262144


class ROSTER_TYPE(UnitBase.ROSTER_TYPE, ConstInjector):
    COMP7_ROSTER = UNIT_MGR_FLAGS.SQUAD | UNIT_MGR_FLAGS.COMP7


class PREBATTLE_TYPE(constants.PREBATTLE_TYPE, ConstInjector):
    COMP7 = 24
    TRAINING_COMP7 = 26


class INVITATION_TYPE(constants.INVITATION_TYPE, ConstInjector):
    COMP7 = PREBATTLE_TYPE.COMP7


class CLIENT_UNIT_CMD(UnitBase.CLIENT_UNIT_CMD, ConstInjector):
    SET_SQUAD_SIZE = 4301


class GameSeasonType(constants.GameSeasonType, ConstInjector):
    COMP7 = 7
