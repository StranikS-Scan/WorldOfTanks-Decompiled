# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/sound_constants.py
from sound_gui_manager import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class Sounds(CONST_CONTAINER):
    RESEARCH_SOUND_SPACE = 'research_preview'
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_RESEARCH_PREVIEW = 'STATE_hangar_place_researches_preview'
    PREVIEW_SOUND_SPACE = 'research_preview'
    SUBVIEW_HANGAR_GENERAL = 'STATE_subview_hangar_general'
    SUBVIEW_HANGAR_GENERAL_ON = 'STATE_subview_hangar_general_on'
    SUBVIEW_HANGAR_GENERAL_OFF = 'STATE_subview_hangar_general_off'
    HANGAR_PLACE_STATE = 'STATE_hangar_place'
    HANGAR_PLACE_GARAGE = 'STATE_hangar_place_garage'


RESEARCH_PREVIEW_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.RESEARCH_SOUND_SPACE, entranceStates={Sounds.STATE_PLACE: Sounds.STATE_PLACE_RESEARCH_PREVIEW}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
STYLE_PREVIEW_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.PREVIEW_SOUND_SPACE, entranceStates={Sounds.SUBVIEW_HANGAR_GENERAL: Sounds.SUBVIEW_HANGAR_GENERAL_ON,
 Sounds.HANGAR_PLACE_STATE: Sounds.HANGAR_PLACE_GARAGE}, exitStates={Sounds.SUBVIEW_HANGAR_GENERAL: Sounds.SUBVIEW_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
VEHICLE_PREVIEW_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.PREVIEW_SOUND_SPACE, entranceStates={Sounds.SUBVIEW_HANGAR_GENERAL: Sounds.SUBVIEW_HANGAR_GENERAL_ON,
 Sounds.HANGAR_PLACE_STATE: Sounds.HANGAR_PLACE_GARAGE}, exitStates={Sounds.SUBVIEW_HANGAR_GENERAL: Sounds.SUBVIEW_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
