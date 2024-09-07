# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/sounds_constants.py
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings

class SOUNDS(CONST_CONTAINER):
    GENERAL_STATE = 'STATE_overlay_hangar_general'
    GENERAL_STATE_ON = 'STATE_overlay_hangar_general_on'
    GENERAL_STATE_OFF = 'STATE_overlay_hangar_general_off'


class WinbackSounds(CONST_CONTAINER):
    REWARD_SCREEN = 'gui_reward_screen_general'


GENERAL_SOUND_SPACE = CommonSoundSpaceSettings(name='winback_general', entranceStates={SOUNDS.GENERAL_STATE: SOUNDS.GENERAL_STATE_ON}, exitStates={SOUNDS.GENERAL_STATE: SOUNDS.GENERAL_STATE_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
REWARD_SOUND_SPACE = CommonSoundSpaceSettings(name='winback_reward', entranceStates={SOUNDS.GENERAL_STATE: SOUNDS.GENERAL_STATE_ON}, exitStates={SOUNDS.GENERAL_STATE: SOUNDS.GENERAL_STATE_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=WinbackSounds.REWARD_SCREEN, exitEvent='')
