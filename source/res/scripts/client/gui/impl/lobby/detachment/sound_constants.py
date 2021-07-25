# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/sound_constants.py
from sound_gui_manager import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER
INSTRUCTOR_VIEW_EVENT = 'detachment_instructor_view'

class BarracksSounds(CONST_CONTAINER):
    COMMON_SOUND_SPACE = 'barracks'
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_BARRACKS = 'STATE_hangar_place_barracks'
    EVENT_BARRACKS_ENTER = 'detachment_enter'
    EVENT_BARRACKS_EXIT = 'detachment_exit'


BARRACKS_SOUND_SPACE = CommonSoundSpaceSettings(name=BarracksSounds.COMMON_SOUND_SPACE, entranceStates={BarracksSounds.STATE_PLACE: BarracksSounds.STATE_PLACE_BARRACKS}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=BarracksSounds.EVENT_BARRACKS_ENTER, exitEvent=BarracksSounds.EVENT_BARRACKS_EXIT)

class HangarOverlaySounds(CONST_CONTAINER):
    COMMON_SOUND_SPACE = 'overlay_hangar'
    STATE_PLACE = 'STATE_overlay_hangar_general'
    STATE_PLACE_OVERLAY_ON = 'STATE_overlay_hangar_general_on'
    STATE_PLACE_OVERLAY_OFF = 'STATE_overlay_hangar_general_off'


HANGAR_OVERLAY_SOUND_SPACE = CommonSoundSpaceSettings(name=HangarOverlaySounds.COMMON_SOUND_SPACE, entranceStates={HangarOverlaySounds.STATE_PLACE: HangarOverlaySounds.STATE_PLACE_OVERLAY_ON}, exitStates={HangarOverlaySounds.STATE_PLACE: HangarOverlaySounds.STATE_PLACE_OVERLAY_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
