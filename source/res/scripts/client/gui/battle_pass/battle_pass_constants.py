# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/battle_pass_constants.py
from enum import Enum, unique
from constants import ARENA_BONUS_TYPE
MIN_LEVEL = 1

class BonusesLayoutConsts(object):
    PRIORITY_KEY = 'priority'
    VISIBILITY_KEY = 'isVisible'
    OVERRIDE_KEY = 'override'
    ID_KEY = 'id'
    LEVEL_KEY = 'level'
    BIG_ICON_KEY = 'bigIcon'
    MAIN_KEYS = (PRIORITY_KEY, VISIBILITY_KEY, BIG_ICON_KEY)
    INT_VALUES = (PRIORITY_KEY,)
    BOOL_VALUES = (VISIBILITY_KEY,)


@unique
class ChapterState(Enum):
    ACTIVE = 'active'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    NOT_STARTED = 'notStarted'
    DISABLED = 'disabled'


SUPPORTED_ARENA_BONUS_TYPES = [ARENA_BONUS_TYPE.REGULAR,
 ARENA_BONUS_TYPE.COMP7,
 ARENA_BONUS_TYPE.EPIC_BATTLE,
 ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO,
 ARENA_BONUS_TYPE.RANKED,
 ARENA_BONUS_TYPE.FORT_BATTLE_2,
 ARENA_BONUS_TYPE.SORTIE_2,
 ARENA_BONUS_TYPE.VERSUS_AI]
HAS_DAILY_ARENA_BONUS_TYPES = {ARENA_BONUS_TYPE.REGULAR, ARENA_BONUS_TYPE.RANKED}
