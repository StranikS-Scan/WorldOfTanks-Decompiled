# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/advent_calendar_v2/advent_calendar_v2_sound.py
from sound_gui_manager import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class AdventCalendarV2Sounds(CONST_CONTAINER):
    ADVENT_CALENDAR_NAME = 'advent_calendar_sound'
    ADVENT_CALENDAR_STATE = 'STATE_ext_hangar_newyear_place'
    ADVENT_CALENDAR_STATE_ON = 'STATE_ext_hangar_newyear_place_gift_system'
    ADVENT_CALENDAR_STATE_OFF = 'STATE_ext_hangar_newyear_place_hangar'
    ADVENT_CALENDAR_ENTER = 'adv_enter'
    ADVENT_CALENDAR_CLOSE = 'adv_exit'


ADVENT_CALENDAR_V2_MAIN_WINDOW_SOUND = CommonSoundSpaceSettings(name=AdventCalendarV2Sounds.ADVENT_CALENDAR_NAME, entranceStates={AdventCalendarV2Sounds.ADVENT_CALENDAR_STATE: AdventCalendarV2Sounds.ADVENT_CALENDAR_STATE_ON}, exitStates={AdventCalendarV2Sounds.ADVENT_CALENDAR_STATE: AdventCalendarV2Sounds.ADVENT_CALENDAR_STATE_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=AdventCalendarV2Sounds.ADVENT_CALENDAR_ENTER, exitEvent=AdventCalendarV2Sounds.ADVENT_CALENDAR_CLOSE)
