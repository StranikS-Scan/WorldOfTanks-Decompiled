# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/common/grinch_progression_common/grinch_progression_constants.py
import constants
from enum import Enum
from constants_utils import ConstInjector

class Configs(Enum):
    GRINCH_PROGRESSION_CONFIG = 'grinch_progression_config'


class ProgressionStates(Enum):
    NOT_STARTED = 'not_started'
    FINISHED = 'finished'
    IN_PROGRESS = 'in_progress'
    OFF_CHAPTER = 'off_chapter'
    SUSPENDED = 'suspended'
    RESUME = 'resume'


class REQUEST_COOLDOWN(constants.REQUEST_COOLDOWN, ConstInjector):
    CMD_GP_OPEN_STEP = 3.0
