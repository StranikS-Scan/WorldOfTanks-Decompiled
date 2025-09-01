# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/common/comp7_light_constants.py
import constants
import enum
from constants_utils import ConstInjector
import UnitBase

class Configs(enum.Enum):
    COMP7_LIGHT_CONFIG = 'comp7_light_config'


COMP7_LIGHT_INBATTLE_CONFIGS = (Configs.COMP7_LIGHT_CONFIG.value,)
BATTLE_MODE_VEH_TAGS_EXCEPT_COMP7_LIGHT = constants.BATTLE_MODE_VEHICLE_TAGS - {'comp7_light'}

class ARENA_GUI_TYPE(constants.ARENA_GUI_TYPE, ConstInjector):
    COMP7_LIGHT = 35


class PREBATTLE_TYPE(constants.PREBATTLE_TYPE, ConstInjector):
    COMP7_LIGHT = 27


class INVITATION_TYPE(constants.INVITATION_TYPE, ConstInjector):
    COMP7_LIGHT = PREBATTLE_TYPE.COMP7_LIGHT


class UNIT_MGR_FLAGS(UnitBase.UNIT_MGR_FLAGS, ConstInjector):
    COMP7_LIGHT = 16777216


class ROSTER_TYPE(UnitBase.ROSTER_TYPE, ConstInjector):
    COMP7_LIGHT_ROSTER = UNIT_MGR_FLAGS.SQUAD | UNIT_MGR_FLAGS.COMP7_LIGHT


class GameSeasonType(constants.GameSeasonType, ConstInjector):
    COMP7_LIGHT = 9


class CLIENT_UNIT_CMD(UnitBase.CLIENT_UNIT_CMD, ConstInjector):
    SET_COMP7_LIGHT_SQUAD_SIZE = 4302
