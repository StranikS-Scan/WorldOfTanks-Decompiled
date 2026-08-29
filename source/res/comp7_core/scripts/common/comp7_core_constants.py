# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/common/comp7_core_constants.py
from __future__ import absolute_import
import enum
import constants
from constants_utils import ConstInjector
ROLE_EQUIPMENT_TAG = 'roleEquipment'

class ArenaPrebattlePhase(object):
    NONE = 0
    PREPICK = 1
    VOTING = 2
    PICK = 3


class FINISH_REASON(constants.FINISH_REASON, ConstInjector):
    SURVIVORS_LEFT = 201
    DAMAGE_DEALT = 202
    FIRST_KILL = 203
    DRAW_RESOLVED_REASONS = (SURVIVORS_LEFT, DAMAGE_DEALT, FIRST_KILL)


class SubMode(enum.Enum):
    REGULAR = 'regular'
    NIGHT_MAPS = 'night_maps'


def injectCommonConstants(personality):
    if not any((reason in FINISH_REASON.getExtraAttrs().values() for reason in FINISH_REASON.DRAW_RESOLVED_REASONS)):
        FINISH_REASON.inject(personality)
