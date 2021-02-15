# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/trainings/sound_constants.py
from sound_gui_manager import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class Sounds(CONST_CONTAINER):
    COMMON_SOUND_SPACE = 'trainings'
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_GARAGE = 'STATE_hangar_place_garage'


TRAININGS_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.COMMON_SOUND_SPACE, entranceStates={Sounds.STATE_PLACE: Sounds.STATE_PLACE_GARAGE}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
