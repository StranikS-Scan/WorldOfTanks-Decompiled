# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_reserves/reserves_constants.py
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings

class SOUNDS(CONST_CONTAINER):
    COMMON_SOUND_SPACE = 'personalReserves'
    STATE_PLACE = 'STATE_personal_reserves'
    STATE_PERSONAL_RESERVES_ON = 'STATE_personal_reserves_on'
    STATE_PERSONAL_RESERVES_OFF = 'STATE_personal_reserves_off'
    ENTER_EVENT = 'personal_reserves'


PERSONAL_RESERVES_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.COMMON_SOUND_SPACE, entranceStates={SOUNDS.STATE_PLACE: SOUNDS.STATE_PERSONAL_RESERVES_ON}, exitStates={SOUNDS.STATE_PLACE: SOUNDS.STATE_PERSONAL_RESERVES_OFF}, persistentSounds=(SOUNDS.ENTER_EVENT,), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
