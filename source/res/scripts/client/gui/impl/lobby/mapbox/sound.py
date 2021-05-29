# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mapbox/sound.py
from enum import Enum
from sound_gui_manager import CommonSoundSpaceSettings

class Sounds(Enum):
    OVERLAY_HANGAR_GENERAL = 'STATE_overlay_hangar_general'
    OVERLAY_HANGAR_GENERAL_ON = 'STATE_overlay_hangar_general_on'
    OVERLAY_HANGAR_GENERAL_OFF = 'STATE_overlay_hangar_general_off'


def getMapboxViewSoundSpace(enterEvent='', exitEvent=''):
    return CommonSoundSpaceSettings(name='mapbox_view', entranceStates={Sounds.OVERLAY_HANGAR_GENERAL.value: Sounds.OVERLAY_HANGAR_GENERAL_ON.value}, exitStates={Sounds.OVERLAY_HANGAR_GENERAL.value: Sounds.OVERLAY_HANGAR_GENERAL_OFF.value}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=enterEvent, exitEvent=exitEvent)
