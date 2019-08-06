# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/marathon_constants.py
from shared_utils import CONST_CONTAINER

class MARATHON_FLAG_TOOLTIP_HEADERS(CONST_CONTAINER):
    COUNTDOWN = 'countdown'
    PROGRESS = 'progress'
    TEXT = 'simple_text'


class MARATHON_STATE(CONST_CONTAINER):
    NOT_STARTED = 0
    IN_PROGRESS = 1
    FINISHED = 3
    SUSPENDED = 4
    DISABLED = 5
    UNKNOWN = 6
    ENABLED_STATE = (NOT_STARTED, IN_PROGRESS, FINISHED)
    DISABLED_STATE = (SUSPENDED, DISABLED, UNKNOWN)


class MARATHON_WARNING(CONST_CONTAINER):
    WRONG_VEH_TYPE = 'veh_type'
    WRONG_BATTLE_TYPE = 'battle_type'
    NONE = ''


ZERO_TIME = 0.0
