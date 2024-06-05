# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/sound_constants.py
from sound_gui_manager import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class SOUNDS(CONST_CONTAINER):
    COMMON_SOUND_SPACE = 'achievements'
    ACHIEVEMENTS_ENTER = 'achievements_enter'
    ACHIEVEMENTS_EXIT = 'achievements_exit'
    STATE_PLACE_ACHIEVEMENTS = 'STATE_hangar_place_achievements'
    STATE_PLACE = 'STATE_hangar_place'


ACHIEVEMENTS_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.COMMON_SOUND_SPACE, entranceStates={SOUNDS.STATE_PLACE: SOUNDS.STATE_PLACE_ACHIEVEMENTS}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=SOUNDS.ACHIEVEMENTS_ENTER, exitEvent=SOUNDS.ACHIEVEMENTS_EXIT)
ACHIEVEMENTS_REWARD_SCREEN_EXIT_EVENT = 'ach_reward_screen_exit'
