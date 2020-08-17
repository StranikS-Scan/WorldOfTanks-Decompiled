# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ten_year_countdown_config.py
from enum import Enum
from constants import IS_CHINA

class EventBlockStates(Enum):
    ACTIVE = 'active'
    PASSIVE = 'passive'
    NOT_STARTED = 'notStarted'
    FINISHED = 'finished'


EVENT_BLOCKS_COUNT = 5 if not IS_CHINA else 1
FIRST_BLOCK_NUMBER = 1
EVENT_BADGE_NAME = '10YC_POINTS'
BLOCK_TOKEN_TEMPLATE = '10YC_CH{}_CLEAR'
EVENT_BADGE_MISSION_ID = '10YC_BADGE_CLEAR'
EVENT_STYLE_MISSION_ID = '10YC_3DS_CLEAR'
TEN_YEAR_COUNTDOWN_QUEST_TOKEN_PREFIX = '10YC_CH'
TEN_YEAR_COUNTDOWN_QUEST_TOKEN_POSTFIX = '_CLEAR'
