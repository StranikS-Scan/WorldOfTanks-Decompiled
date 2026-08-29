# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/prebattle_highlights/constants.py
from enum import Enum
FEATURE = 'prebattle_highlights'

class PrebattleHighlightsLogAction(Enum):
    VIEWED = 'viewed'
    COLLAPSE = 'collapse'


class PrebattleHighlightsLogKeys(Enum):
    PBH = 'pbh'
    PBH_OUT_OF_FOCUS = 'pbh_out_of_focus'
    FULLY_VIEWED = 'fully_viewed'
    ESC = 'esc'
    SETTINGS_PBH = 'settings_pbh'
    SETTINGS_HISTORICAL = 'settings_historical'
    NOT_ENOUGH_TIME = 'not_enough_time'
