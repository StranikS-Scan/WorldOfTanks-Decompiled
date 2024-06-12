# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/sounds.py
import WWISE
from enum import Enum
from sound_gui_manager import CommonSoundSpaceSettings
from gui.Scaleform.daapi.view.lobby.vehicle_preview.sound_constants import Sounds as VehiclePreviewSounds

class Sounds(Enum):
    INTRO_NAME = 'early_access_intro'
    OVERLAY_HANGAR_FILTERED = 'STATE_hangar_filtered'
    OVERLAY_HANGAR_FILTERED_ON = 'STATE_hangar_filtered_on'


def setResearchesPreviewSoundState():
    WWISE.WW_setState(VehiclePreviewSounds.STATE_PLACE, VehiclePreviewSounds.STATE_PLACE_RESEARCH_PREVIEW)


EARLY_ACCESS_INTRO_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.INTRO_NAME.value, entranceStates={Sounds.OVERLAY_HANGAR_FILTERED.value: Sounds.OVERLAY_HANGAR_FILTERED_ON.value}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
