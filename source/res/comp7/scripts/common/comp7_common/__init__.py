# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/common/comp7_common/__init__.py
import constants
from constants_utils import addArenaGuiTypesFromExtension, addPrebattleTypesFromExtension, initSquadCommonTypes
from comp7_common import comp7_constants
from constants import PREBATTLE_TYPE

def injectConsts(personality):
    addArenaGuiTypesFromExtension(comp7_constants.ARENA_GUI_TYPE, personality)
    addPrebattleTypesFromExtension(comp7_constants.PREBATTLE_TYPE, personality)
    constants.INBATTLE_CONFIGS.extend(comp7_constants.COMP7_INBATTLE_CONFIGS)
    PREBATTLE_TYPE.TRAININGS += (comp7_constants.PREBATTLE_TYPE.TRAINING_COMP7,)


def injectSquadConsts(personality):
    initSquadCommonTypes(comp7_constants, personality)
    constants.INVITATION_TYPE.TYPES_WITH_EXTRA_DATA += (comp7_constants.INVITATION_TYPE.COMP7,)
