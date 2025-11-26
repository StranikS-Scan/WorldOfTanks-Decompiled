# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/common/advent_calendar_common/advent_calendar_constants.py
GAME_PARAMS_KEY = 'new_advent_calendar_config'
ADVENT_POINTS_TOKEN = 'advent:points'

class DoorMarkType(object):
    WDR = 'wdr'
    NY_START = 'ny_start'
    NY_MODE = 'ny_mode'
    NONE = 'none'
    RANGE = [WDR, NY_START, NY_MODE]
