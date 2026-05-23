# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/sound_constants.py
from __future__ import absolute_import
from sound_gui_manager import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class Sounds(CONST_CONTAINER):
    COMMON_SOUND_SPACE = 'techtree'
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_TECHTREE = 'STATE_hangar_place_research'
    AMBIENT = 'researches_ambience'
    MUSIC = 'researches_music'
    RESET = 'researches_music_reset'


TECHTREE_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.COMMON_SOUND_SPACE, entranceStates={Sounds.STATE_PLACE: Sounds.STATE_PLACE_TECHTREE}, exitStates={}, persistentSounds=(Sounds.MUSIC, Sounds.AMBIENT), stoppableSounds=(), priorities=(), autoStart=True, exitEvent=Sounds.RESET)
