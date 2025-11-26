# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/lobby/feature/sound_helper.py
from __future__ import absolute_import
from sound_gui_manager import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class AdventCalendarSounds(CONST_CONTAINER):
    ADVENT_CALENDAR_NAME = 'advent_calendar_sound'
    OVERLAY_HANGAR_GENERAL = 'STATE_overlay_hangar_general'
    OVERLAY_HANGAR_GENERAL_ON = 'STATE_overlay_hangar_general_on'
    OVERLAY_HANGAR_GENERAL_OFF = 'STATE_overlay_hangar_general_off'
    ADVENT_CALENDAR_ENTER = 'adv_enter'
    ADVENT_CALENDAR_CLOSE = 'adv_exit'


ADVENT_CALENDAR_MAIN_WINDOW_SOUND = CommonSoundSpaceSettings(name=AdventCalendarSounds.ADVENT_CALENDAR_NAME, entranceStates={AdventCalendarSounds.OVERLAY_HANGAR_GENERAL: AdventCalendarSounds.OVERLAY_HANGAR_GENERAL_ON}, exitStates={AdventCalendarSounds.OVERLAY_HANGAR_GENERAL: AdventCalendarSounds.OVERLAY_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=AdventCalendarSounds.ADVENT_CALENDAR_ENTER, exitEvent=AdventCalendarSounds.ADVENT_CALENDAR_CLOSE)
