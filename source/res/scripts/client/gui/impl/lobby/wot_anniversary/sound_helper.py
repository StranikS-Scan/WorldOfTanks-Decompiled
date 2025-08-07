# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wot_anniversary/sound_helper.py
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings

class SOUNDS(CONST_CONTAINER):
    MAIN_VIEW_ENTER_EVENT = 'ev_bday_2025_enter'
    MAIN_VIEW_EXIT_EVENT = 'ev_bday_2025_exit'
    WELCOME_VIEW_ENTER_EVENT = 'ev_bday_2025_intro'
    STATE_HANGAR_FILTERED = 'STATE_hangar_filtered'
    STATE_HANGAR_FILTERED_ON = 'STATE_hangar_filtered_on'
    STATE_HANGAR_FILTERED_OFF = 'STATE_hangar_filtered_off'
    STATE_VIDEO_OVERLAY = 'STATE_video_overlay'
    STATE_VIDEO_OVERLAY_ON = 'STATE_video_overlay_on'
    STATE_VIDEO_OVERLAY_OFF = 'STATE_video_overlay_off'


def getMainSoundSpace():
    return CommonSoundSpaceSettings(name='wot_anniversary_main_view', entranceStates={SOUNDS.STATE_HANGAR_FILTERED: SOUNDS.STATE_HANGAR_FILTERED_ON}, exitStates={SOUNDS.STATE_HANGAR_FILTERED: SOUNDS.STATE_HANGAR_FILTERED_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=SOUNDS.MAIN_VIEW_ENTER_EVENT, exitEvent=SOUNDS.MAIN_VIEW_EXIT_EVENT)


def getVideoViewSoundSpace():
    return CommonSoundSpaceSettings(name='wot_anniversary_video_view', entranceStates={SOUNDS.STATE_VIDEO_OVERLAY: SOUNDS.STATE_VIDEO_OVERLAY_ON}, exitStates={SOUNDS.STATE_VIDEO_OVERLAY: SOUNDS.STATE_VIDEO_OVERLAY_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
