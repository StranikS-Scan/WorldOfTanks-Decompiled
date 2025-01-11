# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/sound_constants.py
from sound_gui_manager import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class Sounds(CONST_CONTAINER):
    SOUND_SPACE = 'paragons'
    SOUND_PLACE_HANGAR = 'STATE_hangar_place'
    SOUND_HANGAR_PLACE_PARAGONS = 'STATE_hangar_place_paragons'
    SOUND_PREVIEW_PLACE_PARAGONS = 'STATE_hangar_place_paragons_preview'
    STATE_PLACE_TECHTREE = 'STATE_hangar_place_research'
    ENTER_SOUND_EVENT = 'paragons_hangar_enter'
    EXIT_SOUND_EVENT = 'paragons_hangar_exit'
    SOUND_SLIDE_IN = 'dq_widget_slide_in'


PARAGONS_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.SOUND_SPACE, entranceStates={Sounds.SOUND_PLACE_HANGAR: Sounds.SOUND_HANGAR_PLACE_PARAGONS}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=Sounds.ENTER_SOUND_EVENT, exitEvent=Sounds.EXIT_SOUND_EVENT)
PARAGONS_PREVIEW_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.SOUND_SPACE, entranceStates={Sounds.SOUND_PLACE_HANGAR: Sounds.SOUND_PREVIEW_PLACE_PARAGONS}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=Sounds.ENTER_SOUND_EVENT, exitEvent=Sounds.EXIT_SOUND_EVENT)
PARAGONS_RESET_BRANCH_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.SOUND_SPACE, entranceStates={Sounds.SOUND_PLACE_HANGAR: Sounds.SOUND_HANGAR_PLACE_PARAGONS}, exitStates={Sounds.SOUND_PLACE_HANGAR: Sounds.STATE_PLACE_TECHTREE}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=Sounds.ENTER_SOUND_EVENT, exitEvent=Sounds.EXIT_SOUND_EVENT)
