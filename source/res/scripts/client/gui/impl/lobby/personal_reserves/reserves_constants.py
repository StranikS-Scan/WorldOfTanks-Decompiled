# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_reserves/reserves_constants.py
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings

class SOUNDS(CONST_CONTAINER):
    COMMON_SOUND_SPACE = 'personalReserves'
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_PERSONAL_RESERVES = 'STATE_hangar_place_personal_reserves'
    STATE_PLACE_HANGAR = 'STATE_hangar_place_garage'
    ENTER_EVENT = 'personal_reserves'


PERSONAL_RESERVES_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.COMMON_SOUND_SPACE, entranceStates={SOUNDS.STATE_PLACE: SOUNDS.STATE_PLACE_PERSONAL_RESERVES}, exitStates={SOUNDS.STATE_PLACE: SOUNDS.STATE_PLACE_HANGAR}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=SOUNDS.ENTER_EVENT, exitEvent='')
