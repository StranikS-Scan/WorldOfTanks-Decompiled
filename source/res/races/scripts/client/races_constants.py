# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races_constants.py
from enum import Enum
RACES_FIRST_WIN_QUEST = 'races_first_win'

class EVENT_STATES(Enum):
    START = 0
    FINISH = 1
    SUSPEND = 2
    RESUME = 3
