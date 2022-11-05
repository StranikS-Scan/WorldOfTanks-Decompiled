# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/fun_sounds.py
from sound_gui_manager import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class FunSounds(CONST_CONTAINER):
    HANGAR_PLACE_STATE = 'STATE_hangar_place'
    HANGAR_PLACE_TASKS = 'STATE_hangar_place_tasks'
    PROGRESSION_SPACE_NAME = 'fun_progression_view'
    PROGRESSION_ENTER_EVENT = 'ev_fep_tasks_enter'
    PROGRESSION_EXIT_EVENT = 'ev_fep_tasks_exit'


FUN_PROGRESSION_SOUND_SPACE = CommonSoundSpaceSettings(name=FunSounds.PROGRESSION_SPACE_NAME, entranceStates={FunSounds.HANGAR_PLACE_STATE: FunSounds.HANGAR_PLACE_TASKS}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=FunSounds.PROGRESSION_ENTER_EVENT, exitEvent=FunSounds.PROGRESSION_EXIT_EVENT)
