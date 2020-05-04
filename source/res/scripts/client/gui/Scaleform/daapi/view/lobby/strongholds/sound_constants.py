# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/strongholds/sound_constants.py
from gui.Scaleform.framework.entities.view_sound import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class SOUNDS(CONST_CONTAINER):
    COMMON_SOUND_SPACE = 'stronghold'
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_CLANS = 'STATE_hangar_place_clans'
    ENTER = 'clans_enter'


STRONGHOLD_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.COMMON_SOUND_SPACE, entranceStates={SOUNDS.STATE_PLACE: SOUNDS.STATE_PLACE_CLANS}, exitStates={}, persistentSounds=(SOUNDS.ENTER,), stoppableSounds=(), priorities=(), autoStart=True)
