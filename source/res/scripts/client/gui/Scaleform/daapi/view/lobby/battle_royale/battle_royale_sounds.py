# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/battle_royale_sounds.py
from gui.Scaleform.framework.entities.View import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class Sounds(CONST_CONTAINER):
    OVERLAY_SPACE_NAME = 'battle_royale_overlay'
    OVERLAY_HANGAR_GENERAL = 'STATE_overlay_hangar_general'
    OVERLAY_HANGAR_GENERAL_ON = 'STATE_overlay_hangar_general_on'
    OVERLAY_HANGAR_GENERAL_OFF = 'STATE_overlay_hangar_general_off'
    MAIN_PAGE_SPACE_NAME = 'battle_royale_main_page'
    MAIN_PAGE_STATE = 'STATE_gamemode_progress_page'
    MAIN_PAGE_STATE_ON = 'STATE_gamemode_progress_page_on'
    MAIN_PAGE_STATE_OFF = 'STATE_gamemode_progress_page_off'
    VEHILCE_INFO_SPACE_NAME = 'battle_royale_vehicle_info'
    VEHILCE_INFO_STATE = 'STATE_hangar_filtered'
    VEHILCE_INFO_STATE_ON = 'STATE_hangar_filtered_on'
    VEHILCE_INFO_STATE_OFF = 'STATE_hangar_filtered_off'


BATTLE_ROYALE_PAGE_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.MAIN_PAGE_SPACE_NAME, entranceStates={Sounds.MAIN_PAGE_STATE: Sounds.MAIN_PAGE_STATE_ON}, exitStates={Sounds.MAIN_PAGE_STATE: Sounds.MAIN_PAGE_STATE_OFF,
 Sounds.OVERLAY_HANGAR_GENERAL: Sounds.OVERLAY_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
BATTLE_ROYALE_OVERLAY_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.OVERLAY_SPACE_NAME, entranceStates={Sounds.OVERLAY_HANGAR_GENERAL: Sounds.OVERLAY_HANGAR_GENERAL_ON}, exitStates={Sounds.OVERLAY_HANGAR_GENERAL: Sounds.OVERLAY_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
BATTLE_ROYALE_VEHICLE_INFO_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.VEHILCE_INFO_SPACE_NAME, entranceStates={Sounds.VEHILCE_INFO_STATE: Sounds.VEHILCE_INFO_STATE_ON}, exitStates={Sounds.VEHILCE_INFO_STATE: Sounds.VEHILCE_INFO_STATE_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
