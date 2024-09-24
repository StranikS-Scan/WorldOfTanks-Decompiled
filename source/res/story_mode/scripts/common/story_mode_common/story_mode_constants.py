# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/common/story_mode_common/story_mode_constants.py
import typing
import enum
from constants import ARENA_BONUS_TYPE, ARENA_GUI_TYPE
EXTENSION_NAME = 'story_mode'
LOGGER_NAME = 'story_mode'
DEFAULT_BATTLES_LIMIT = 500
BATTLES_LIMIT_KEY = 'stats/story_mode/battlesLimit'
PLAYERS_COUNT_KEY = 'stats/story_mode/Queue{}Players'
PLAYER_BATTLES_COUNT_KEY = 'stats/story_mode/Queue{}PlayerBattlesCount'
AVG_WAIT_TIME_KEY = 'stats/story_mode/Queue{}AvgWaitTime'
SM_CONGRATULATIONS_MESSAGE = 'StoryModeCongratulationsMessage'
STORY_MODE_BONUS_TYPES = (ARENA_BONUS_TYPE.STORY_MODE_ONBOARDING, ARENA_BONUS_TYPE.STORY_MODE_REGULAR)
STORY_MODE_GUI_TYPE_BY_BONUS_TYPE = {ARENA_BONUS_TYPE.STORY_MODE_ONBOARDING: ARENA_GUI_TYPE.STORY_MODE_ONBOARDING,
 ARENA_BONUS_TYPE.STORY_MODE_REGULAR: ARENA_GUI_TYPE.STORY_MODE_REGULAR}
EVENT_NAME = 'story_mode_dday'

class PRIORITY(enum.IntEnum):
    HIGH = 0
    MEDIUM = 1
    LOW = 2


@enum.unique
class MissionsDifficulty(str, enum.Enum):
    UNDEFINED = ''
    NORMAL = 'normal'
    HARD = 'hard'

    @classmethod
    def getDifficultiesByBattles(cls, battlesCount):
        hard = {cls.HARD}
        other = set(cls) - hard
        return hard if battlesCount > HARD_DIFFICULTY_BATTLES_COUNT else other


class MissionType(str, enum.Enum):
    ONBOARDING = 'onboarding'
    REGULAR = 'regular'
    EVENT = 'event'


HARD_DIFFICULTY_BATTLES_COUNT = 1000
PROGRESS_PDATA_KEY = 'progress'
STORY_MODE_PDATA_KEY = 'storyMode'
UNDEFINED_MISSION_ID = -1
FIRST_MISSION_ID = 1
FIRST_MISSION_TASK_ID = 1
LONG_INT_HALF_SHIFT = 32
STORY_MODE_AB_FEATURE = 'storyMode'
DISABLE_REGULAR_OPERATIONS = 'disableRegularOperations'
