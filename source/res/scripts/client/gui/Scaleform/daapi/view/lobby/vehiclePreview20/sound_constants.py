# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/sound_constants.py
from gui.Scaleform.framework.entities.View import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class Sounds(CONST_CONTAINER):
    RESEARCH_SOUND_SPACE = 'research_preview'
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_RESEARCH_PREVIEW = 'STATE_hangar_place_researches_preview'
    STYLE_SOUND_SPACE = 'research_preview'
    OVERLAY_HANGAR_GENERAL = 'STATE_overlay_hangar_general'
    OVERLAY_HANGAR_GENERAL_ON = 'STATE_overlay_hangar_general_on'
    OVERLAY_HANGAR_GENERAL_OFF = 'STATE_overlay_hangar_general_off'
    HANGAR_PLACE_STATE = 'STATE_hangar_place'
    HANGAR_PLACE_GARAGE = 'STATE_hangar_place_garage'


RESEARCH_PREVIEW_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.RESEARCH_SOUND_SPACE, entranceStates={Sounds.STATE_PLACE: Sounds.STATE_PLACE_RESEARCH_PREVIEW}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
STYLE_PREVIEW_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.STYLE_SOUND_SPACE, entranceStates={Sounds.OVERLAY_HANGAR_GENERAL: Sounds.OVERLAY_HANGAR_GENERAL_ON,
 Sounds.HANGAR_PLACE_STATE: Sounds.HANGAR_PLACE_GARAGE}, exitStates={Sounds.OVERLAY_HANGAR_GENERAL: Sounds.OVERLAY_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
