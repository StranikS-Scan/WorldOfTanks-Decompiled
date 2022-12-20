# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: survey/scripts/common/SurveyConstants.py
from enum import IntEnum
CMD_SURVEY_RES = 22001

class SURVEY_ANSWERS(IntEnum):
    CANCELED = -3
    WORST = -2
    BAD = -1
    NEUTRAL = 0
    GOOD = 1
    BEST = 2
