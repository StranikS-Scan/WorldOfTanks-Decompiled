# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/fun_constants.py
from enum import unique, Enum
from gui.periodic_battles.models import PeriodType
FEP_MODE_ITEMS_QUEST_ID = 'FEP_mode_items'
FEP_PROGRESSION_PREFIX = 'FEP_progression_'
FEP_PROGRESSION_TRIGGER_QUEST_ID = FEP_PROGRESSION_PREFIX + 'trigger'
FEP_PROGRESSION_EXECUTOR_QUEST_ID = FEP_PROGRESSION_PREFIX + 'executor'
PROGRESSION_COUNTER_TEMPLATE = FEP_PROGRESSION_PREFIX + 'counter_{}'
PROGRESSION_EXECUTOR_TEMPLATE = FEP_PROGRESSION_EXECUTOR_QUEST_ID + '_{}_{}'
PROGRESSION_TRIGGER_TEMPLATE = FEP_PROGRESSION_TRIGGER_QUEST_ID + '_{}'

class FunSubModesState(object):
    UNDEFINED = 0
    BEFORE_SEASON = 1
    BETWEEN_SEASONS = 2
    AFTER_SEASON = 3
    AVAILABLE = 5
    FROZEN = 6
    SINGLE_FROZEN = 7
    NOT_AVAILABLE = 8
    NOT_AVAILABLE_END = 9
    BEFORE_STATES = {BEFORE_SEASON, BETWEEN_SEASONS}
    INNER_STATES = {AVAILABLE,
     FROZEN,
     SINGLE_FROZEN,
     NOT_AVAILABLE,
     NOT_AVAILABLE_END}
    HIDDEN_ENTRY_STATES = {UNDEFINED,
     AFTER_SEASON,
     SINGLE_FROZEN,
     FROZEN}
    HIDDEN_SELECTOR_STATES = {UNDEFINED, AFTER_SEASON}


STATE_TO_SINGLE = {FunSubModesState.FROZEN: FunSubModesState.SINGLE_FROZEN}

class FunNotificationType(object):
    NEW_SUB_MODES = 'newSubModes'
    STOP_SUB_MODES = 'stopSubModes'
    STOP_ALL_SUB_MODES = 'stopAllSubModes'
    SWITCH_OFF_SUB_MODES = 'switchOffSubModes'
    SWITCH_ON_SUB_MODES = 'switchOnSubModes'
    NEW_PROGRESSION = 'newProgression'


class FunTimersShifts(object):
    PROGRESSION = 0.5
    NOTIFICATIONS = 1.0
    SUB_MODE = 0.5


@unique
class FunNotificationSubModeState(Enum):
    UNDEFINED = PeriodType.UNDEFINED
    BEFORE_SEASON = PeriodType.BEFORE_SEASON
    BETWEEN_SEASONS = PeriodType.BETWEEN_SEASONS
    AFTER_SEASON = PeriodType.AFTER_SEASON
    AVAILABLE = PeriodType.AVAILABLE
    FROZEN = PeriodType.FROZEN


@unique
class FunSubModeBroadcast(Enum):
    START_NOTIFICATION = 'startNotification'
    STOP_NOTIFICATION = 'stopNotification'
