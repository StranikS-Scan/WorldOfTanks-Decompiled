# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/wot_plus/sound_constants.py
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings

class SOUNDS(CONST_CONTAINER):
    INFO_PAGE_NAME = 'wot_plus_info_page'
    VEHICLE_RENTAL_PAGE_NAME = 'vehicle_rental_page'
    OVERLAY_HANGAR_GENERAL = 'STATE_overlay_hangar_general'
    OVERLAY_HANGAR_GENERAL_ON = 'STATE_overlay_hangar_general_on'
    OVERLAY_HANGAR_GENERAL_OFF = 'STATE_overlay_hangar_general_off'


WOT_PLUS_INFO_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.INFO_PAGE_NAME, entranceStates={SOUNDS.OVERLAY_HANGAR_GENERAL: SOUNDS.OVERLAY_HANGAR_GENERAL_ON}, exitStates={SOUNDS.OVERLAY_HANGAR_GENERAL: SOUNDS.OVERLAY_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
VEHICLE_RENTAL_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.VEHICLE_RENTAL_PAGE_NAME, entranceStates={SOUNDS.OVERLAY_HANGAR_GENERAL: SOUNDS.OVERLAY_HANGAR_GENERAL_ON}, exitStates={SOUNDS.OVERLAY_HANGAR_GENERAL: SOUNDS.OVERLAY_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
