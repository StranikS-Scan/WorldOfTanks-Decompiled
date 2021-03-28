# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/strongholds/sound_constants.py
from sound_gui_manager import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class SOUNDS(CONST_CONTAINER):
    STRONGHOLD_SOUND_SPACE = 'stronghold'
    STRONGHOLD_ADS_SOUND_SPACE = 'stronghold_ads'
    STATE_HANGAR_PLACE = 'STATE_hangar_place'
    STATE_HANGAR_PLACE_CLANS = 'STATE_hangar_place_clans'
    STATE_HP_CLANS_INSIDE = 'STATE_hp_clans_inside'
    STATE_HP_CLANS_INSIDE_MAIN = 'STATE_hp_clans_inside_main'
    STATE_HP_CLANS_INSIDE_ADS = 'STATE_hp_clans_inside_ads'
    ENTER = 'clans_enter'
    ADS_ENTER = 'ads_enter'
    ADS_EXIT = 'ads_exit'


STRONGHOLD_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.STRONGHOLD_SOUND_SPACE, entranceStates={SOUNDS.STATE_HANGAR_PLACE: SOUNDS.STATE_HANGAR_PLACE_CLANS}, exitStates={}, persistentSounds=(SOUNDS.ENTER,), stoppableSounds=(), priorities=(), autoStart=True)
STRONGHOLD_ADS_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.STRONGHOLD_ADS_SOUND_SPACE, entranceStates={SOUNDS.STATE_HP_CLANS_INSIDE: SOUNDS.STATE_HP_CLANS_INSIDE_ADS}, exitStates={SOUNDS.STATE_HP_CLANS_INSIDE: SOUNDS.STATE_HP_CLANS_INSIDE_MAIN}, enterEvent=SOUNDS.ADS_ENTER, exitEvent=SOUNDS.ADS_EXIT, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, parentSpace=SOUNDS.STRONGHOLD_SOUND_SPACE)
