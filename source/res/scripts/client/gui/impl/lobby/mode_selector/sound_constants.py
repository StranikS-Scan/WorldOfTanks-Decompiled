# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/sound_constants.py
from sound_gui_manager import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class ModeSelectorSound(CONST_CONTAINER):
    COMMON_SOUND_SPACE = 'mode_selector'
    STATE_PLACE = 'STATE_mode_selector'
    STATE_MODE_SELECTOR_ON = 'STATE_mode_selector_on'
    STATE_MODE_SELECTOR_OFF = 'STATE_mode_selector_off'
    ENTER_EVENT = 'ev_mode_selector_enter'
    EXIT_EVENT = 'ev_mode_selector_exit'


MODE_SELECTOR_SOUND_SPACE = CommonSoundSpaceSettings(name=ModeSelectorSound.COMMON_SOUND_SPACE, entranceStates={ModeSelectorSound.STATE_PLACE: ModeSelectorSound.STATE_MODE_SELECTOR_ON}, exitStates={ModeSelectorSound.STATE_PLACE: ModeSelectorSound.STATE_MODE_SELECTOR_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=ModeSelectorSound.ENTER_EVENT, exitEvent=ModeSelectorSound.EXIT_EVENT)
