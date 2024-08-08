# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wot_anniversary/sound.py
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings

class AnniversarySounds(CONST_CONTAINER):
    HANGAR_OVERLAY_STATE = 'STATE_overlay_hangar_general'
    HANGAR_OVERLAY_STATE_ON = 'STATE_overlay_hangar_general_on'
    HANGAR_OVERLAY_STATE_OFF = 'STATE_overlay_hangar_general_off'
    INTRO_SCREEN_SOUND = 'ev_bday_12_intro'
    REWARD_SCREEN_SOUND = 'ev_bday_12_reward'


WOT_ANNIVERSARY_REWARD_SCREEN_SOUND = CommonSoundSpaceSettings(name='wot_anniversary_reward_screen', entranceStates={AnniversarySounds.HANGAR_OVERLAY_STATE: AnniversarySounds.HANGAR_OVERLAY_STATE_ON}, exitStates={AnniversarySounds.HANGAR_OVERLAY_STATE: AnniversarySounds.HANGAR_OVERLAY_STATE_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=AnniversarySounds.REWARD_SCREEN_SOUND, exitEvent=None)
WOT_ANNIVERSARY_INTRO_SCREEN_SOUND = CommonSoundSpaceSettings(name='wot_anniversary_intro_screen', entranceStates={AnniversarySounds.HANGAR_OVERLAY_STATE: AnniversarySounds.HANGAR_OVERLAY_STATE_ON}, exitStates={AnniversarySounds.HANGAR_OVERLAY_STATE: AnniversarySounds.HANGAR_OVERLAY_STATE_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=AnniversarySounds.INTRO_SCREEN_SOUND, exitEvent=None)
WOT_ANNIVERSARY_WELCOME_WINDOW_SOUND = CommonSoundSpaceSettings(name='wot_anniversary_welcome_screen', entranceStates={AnniversarySounds.HANGAR_OVERLAY_STATE: AnniversarySounds.HANGAR_OVERLAY_STATE_ON}, exitStates={AnniversarySounds.HANGAR_OVERLAY_STATE: AnniversarySounds.HANGAR_OVERLAY_STATE_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=AnniversarySounds.INTRO_SCREEN_SOUND, exitEvent=None)
