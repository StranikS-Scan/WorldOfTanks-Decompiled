# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/tournament/sound_constants.py
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings

class SOUNDS(CONST_CONTAINER):
    TOURNAMENTS_SOUND_SPACE = 'tournaments'
    STATE_HANGAR_PLACE = 'STATE_hangar_place'
    STATE_HANGAR_PLACE_TOURNAMENTS = 'STATE_hangar_place_tournaments'
    ENTER = 'tournaments_enter'
    EXIT = 'tournaments_exit'


TOURNAMENTS_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.TOURNAMENTS_SOUND_SPACE, entranceStates={SOUNDS.STATE_HANGAR_PLACE: SOUNDS.STATE_HANGAR_PLACE_TOURNAMENTS}, exitStates={}, enterEvent=SOUNDS.ENTER, exitEvent=SOUNDS.EXIT, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
