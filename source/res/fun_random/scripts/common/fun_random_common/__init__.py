# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/common/fun_random_common/__init__.py
import constants
from constants_utils import addArenaGuiTypesFromExtension, initSquadCommonTypes
from fun_random_common import fun_constants

def injectConsts(personality):
    addArenaGuiTypesFromExtension(fun_constants.ARENA_GUI_TYPE, personality)
    constants.INBATTLE_CONFIGS.append(fun_constants.FUN_GAME_PARAMS_KEY)


def injectSquadConsts(personality):
    initSquadCommonTypes(fun_constants, personality)
    constants.INVITATION_TYPE.TYPES_WITH_EXTRA_DATA += (fun_constants.INVITATION_TYPE.FUN_RANDOM,)
