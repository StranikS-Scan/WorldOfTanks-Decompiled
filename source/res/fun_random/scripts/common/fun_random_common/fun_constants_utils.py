# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/common/fun_random_common/fun_constants_utils.py
from fun_random_common.fun_constants import ARENA_GUI_TYPE, FunSubModeImpl, FunProgressionCondition

def addArenaGuiTypesFromExtensionToFunRange(extArenaGuiType):
    extraAttrs = extArenaGuiType.getExtraAttrs()
    extraValues = tuple(extraAttrs.itervalues())
    ARENA_GUI_TYPE.FUN_RANDOM_RANGE += extraValues


def addFunRandomSubModeImpl(extSubModeImpl, personality):
    extraAttrs = extSubModeImpl.getExtraAttrs()
    extraValues = tuple(extraAttrs.itervalues())
    extSubModeImpl.inject(personality)
    FunSubModeImpl.ALL += extraValues


def addFunProgressionConditions(extConditions, personality):
    extraAttrs = extConditions.getExtraAttrs()
    extraValues = tuple(extraAttrs.itervalues())
    extConditions.inject(personality)
    FunProgressionCondition.ALL += extraValues
