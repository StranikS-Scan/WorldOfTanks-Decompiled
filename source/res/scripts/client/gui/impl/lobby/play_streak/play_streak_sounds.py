# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/play_streak/play_streak_sounds.py
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings

class Sounds(CONST_CONTAINER):
    SOUND_PLACE_HANGAR = 'STATE_hangar_place'
    STATE_TASKS_PREVIEW = 'STATE_hangar_place_tasks_preview'


PLAYSTREAK_PREVIEW_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.SOUND_PLACE_HANGAR, entranceStates={Sounds.SOUND_PLACE_HANGAR: Sounds.STATE_TASKS_PREVIEW}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
