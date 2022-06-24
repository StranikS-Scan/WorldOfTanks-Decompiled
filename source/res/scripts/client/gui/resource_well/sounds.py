# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/resource_well/sounds.py
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings

class SOUNDS(CONST_CONTAINER):
    SPACE = 'resource_well_space'
    COMMON_ENTER = 'resources_well_enter'
    COMMON_EXIT = 'resources_well_exit'
    PREVIEW_SPACE = 'resource_well_preview_space'
    PREVIEW_ENTER = 'resources_well_preview_enter'
    PREVIEW_EXIT = 'resources_well_preview_exit'
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_GARAGE = 'STATE_hangar_place_garage'


RESOURCE_WELL_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.SPACE, entranceStates={}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=SOUNDS.COMMON_ENTER, exitEvent=SOUNDS.COMMON_EXIT)
