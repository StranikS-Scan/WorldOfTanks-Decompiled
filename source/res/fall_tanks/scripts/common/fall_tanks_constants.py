# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/common/fall_tanks_constants.py
import constants
from constants_utils import ConstInjector, addArenaGuiTypesFromExtension, addAttackReasonTypesFromExtension, addDamageInfoCodes
from fun_random_common import fun_constants
from fun_random_common.fun_constants_utils import addArenaGuiTypesFromExtensionToFunRange, addFunRandomSubModeImpl, addFunProgressionConditions
CALIBER_TO_IMPULSE_FACTOR = 3.5
POWER_IMPULSE_FACTOR = 1.0
MASS_IMPULSE_FACTOR = 1.0
BASE_MASS = 70.0
MIN_IMPULSE = 100.0
MAX_IMPULSE = 1000.0
VEHICLE_DESTROY_PERIOD = 5.0
EVACUATION_TIME = 5.0

class ARENA_GUI_TYPE(constants.ARENA_GUI_TYPE, ConstInjector):
    FALL_TANKS = 200


class ATTACK_REASON(constants.ATTACK_REASON, ConstInjector):
    _const_type = str
    FALL_TANKS_FINISH = 'fall_tanks_finish'
    FALL_TANKS_FALLING = 'fall_tanks_falling'
    FALL_TANKS_LEAVER = 'fall_tanks_leaver'


class FunSubModeImpl(fun_constants.FunSubModeImpl, ConstInjector):
    FALL_TANKS = 2


class FunProgressionCondition(fun_constants.FunProgressionCondition, ConstInjector):
    _const_type = str
    FINISH_TIME = 'fallTanksFinishTime'
    FINISH_POSITION = 'fallTanksPosition'
    CHECKPOINTS_PASSED = 'fallTanksCheckpointsPassed'
    USED_SKILLS = 'fallTanksUsedSkillsN'


DAMAGE_INFO_CODES_PER_ATTACK_REASON = {ATTACK_REASON.FALL_TANKS_FINISH: 'DEATH_FROM_FALL_TANKS_FINISH',
 ATTACK_REASON.FALL_TANKS_FALLING: 'DEATH_FROM_FALL_TANKS_FALLING',
 ATTACK_REASON.FALL_TANKS_LEAVER: 'DEATH_FROM_FALL_TANKS_LEAVER'}

def injectConsts(personality):
    addArenaGuiTypesFromExtension(ARENA_GUI_TYPE, personality)
    addArenaGuiTypesFromExtensionToFunRange(ARENA_GUI_TYPE)
    constants.ARENA_GUI_TYPE.NON_DESERTION_ARENAS += (ARENA_GUI_TYPE.FALL_TANKS,)
    addAttackReasonTypesFromExtension(ATTACK_REASON, personality)
    addDamageInfoCodes(DAMAGE_INFO_CODES_PER_ATTACK_REASON, personality)
    addFunRandomSubModeImpl(FunSubModeImpl, personality)
    addFunProgressionConditions(FunProgressionCondition, personality)
