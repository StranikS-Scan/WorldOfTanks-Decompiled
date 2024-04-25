# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/sounds_constants.py
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings

class SOUNDS(CONST_CONTAINER):
    GENERAL_STATE = 'STATE_overlay_hangar_general'
    GENERAL_STATE_ON = 'STATE_overlay_hangar_general_on'
    GENERAL_STATE_OFF = 'STATE_overlay_hangar_general_off'


GENERAL_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.GENERAL_STATE, entranceStates={SOUNDS.GENERAL_STATE: SOUNDS.GENERAL_STATE_ON}, exitStates={SOUNDS.GENERAL_STATE: SOUNDS.GENERAL_STATE_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
