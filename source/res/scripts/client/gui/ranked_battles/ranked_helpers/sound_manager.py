# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_helpers/sound_manager.py
import WWISE
from sound_gui_manager import CommonSoundSpaceSettings
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from shared_utils import CONST_CONTAINER

class AmbientType(CONST_CONTAINER):
    NATURE = 1
    HANGAR = 2


class Sounds(CONST_CONTAINER):
    FIRST_SELECT_EVENT = 'gui_rb_rank_Entrance_first'
    SELECT_EVENT = 'gui_rb_rank_Entrance'
    DESELECT_EVENT = 'gui_rb_rank_Exit'
    OVERLAY_SPACE_NAME = 'ranked_overlay'
    OVERLAY_HANGAR_GENERAL = 'STATE_overlay_hangar_general'
    OVERLAY_HANGAR_GENERAL_ON = 'STATE_overlay_hangar_general_on'
    OVERLAY_HANGAR_GENERAL_OFF = 'STATE_overlay_hangar_general_off'
    SUBVIEW_SPACE_NAME = 'ranked_subview'
    SUBVIEW_HANGAR_GENERAL = 'STATE_subview_hangar_general'
    SUBVIEW_HANGAR_GENERAL_ON = 'STATE_subview_hangar_general_on'
    SUBVIEW_HANGAR_GENERAL_OFF = 'STATE_subview_hangar_general_off'
    OVERLAY_HANGAR_FILTERED = 'STATE_hangar_filtered'
    OVERLAY_HANGAR_FILTERED_ON = 'STATE_hangar_filtered_on'
    OVERLAY_HANGAR_FILTERED_OFF = 'STATE_hangar_filtered_off'
    SUBVIEW_HANGAR_FILTERED = 'STATE_subview_hangar_filtered'
    SUBVIEW_HANGAR_FILTERED_ON = 'STATE_subview_hangar_filtered_on'
    SUBVIEW_HANGAR_FILTERED_OFF = 'STATE_subview_hangar_filtered_off'
    HANGAR_PLACE_STATE = 'STATE_hangar_place'
    HANGAR_PLACE_GARAGE = 'STATE_hangar_place_garage'
    MAIN_PAGE_SPACE_NAME = 'ranked_main_page'
    MAIN_PAGE_STATE = 'STATE_gamemode_progress_page'
    MAIN_PAGE_STATE_ON = 'STATE_gamemode_progress_page_on'
    MAIN_PAGE_STATE_OFF = 'STATE_gamemode_progress_page_off'
    MAIN_PAGE_AMBIENT_ON_EVENT = 'gui_rb_rank_progress_page_ambient_Entrance'
    MAIN_PAGE_AMBIENT_OFF_EVENT = 'gui_rb_rank_progress_page_ambient_Exit'
    MAIN_PAGE_AMBIENT_STATE = 'STATE_rank_ambient'
    MAIN_PAGE_AMBIENT_STATE_1 = 'STATE_rank_ambient_01'
    MAIN_PAGE_AMBIENT_STATE_2 = 'STATE_rank_ambient_02'
    PROGRESSION_STATE = 'STATE_rank_level'
    PROGRESSION_STATE_DEFAULT = 'STATE_rank_level_00'
    PROGRESSION_STATE_QUALIFICATION = 'STATE_rank_level_01'
    PROGRESSION_STATE_3_DIVISION = 'STATE_rank_level_02'
    PROGRESSION_STATE_2_DIVISION = 'STATE_rank_level_03'
    PROGRESSION_STATE_1_DIVISION = 'STATE_rank_level_04'
    PROGRESSION_STATE_LEAGUES = 'STATE_rank_level_05'
    PROGRESSION_STATE_SHOP = 'STATE_rank_level_05'


RANKED_MAIN_PAGE_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.MAIN_PAGE_SPACE_NAME, entranceStates={Sounds.HANGAR_PLACE_STATE: Sounds.HANGAR_PLACE_GARAGE,
 Sounds.MAIN_PAGE_STATE: Sounds.MAIN_PAGE_STATE_ON,
 Sounds.MAIN_PAGE_AMBIENT_STATE: Sounds.MAIN_PAGE_AMBIENT_STATE_1}, exitStates={Sounds.MAIN_PAGE_STATE: Sounds.MAIN_PAGE_STATE_OFF,
 Sounds.SUBVIEW_HANGAR_GENERAL: Sounds.SUBVIEW_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=Sounds.MAIN_PAGE_AMBIENT_ON_EVENT, exitEvent=Sounds.MAIN_PAGE_AMBIENT_OFF_EVENT)
RANKED_OVERLAY_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.OVERLAY_SPACE_NAME, entranceStates={Sounds.OVERLAY_HANGAR_GENERAL: Sounds.OVERLAY_HANGAR_GENERAL_ON,
 Sounds.OVERLAY_HANGAR_FILTERED: Sounds.OVERLAY_HANGAR_FILTERED_ON}, exitStates={Sounds.OVERLAY_HANGAR_GENERAL: Sounds.OVERLAY_HANGAR_GENERAL_OFF,
 Sounds.OVERLAY_HANGAR_FILTERED: Sounds.OVERLAY_HANGAR_FILTERED_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
RANKED_SUBVIEW_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.SUBVIEW_SPACE_NAME, entranceStates={Sounds.SUBVIEW_HANGAR_GENERAL: Sounds.SUBVIEW_HANGAR_GENERAL_ON,
 Sounds.SUBVIEW_HANGAR_FILTERED: Sounds.SUBVIEW_HANGAR_FILTERED_ON}, exitStates={Sounds.SUBVIEW_HANGAR_GENERAL: Sounds.SUBVIEW_HANGAR_GENERAL_OFF,
 Sounds.SUBVIEW_HANGAR_FILTERED: Sounds.SUBVIEW_HANGAR_FILTERED_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
_DIVISION_TO_PROGRESSION_SOUND = {RANKEDBATTLES_ALIASES.DIVISIONS_CLASSIFICATION: Sounds.PROGRESSION_STATE_QUALIFICATION,
 RANKEDBATTLES_ALIASES.DIVISIONS_BRONZE: Sounds.PROGRESSION_STATE_3_DIVISION,
 RANKEDBATTLES_ALIASES.DIVISIONS_SILVER: Sounds.PROGRESSION_STATE_2_DIVISION,
 RANKEDBATTLES_ALIASES.DIVISIONS_GOLD: Sounds.PROGRESSION_STATE_1_DIVISION}
_TYPE_TO_AMBIENT = {AmbientType.NATURE: Sounds.MAIN_PAGE_AMBIENT_STATE_1,
 AmbientType.HANGAR: Sounds.MAIN_PAGE_AMBIENT_STATE_2}

class RankedSoundManager(object):
    __slots__ = ('__isFirstEntrance',)

    def __init__(self):
        self.__isFirstEntrance = True

    def clear(self):
        self.__isFirstEntrance = True

    def onSoundModeChanged(self, isRankedSoundMode, initialProgressionState=None):
        if isRankedSoundMode:
            if self.__isFirstEntrance:
                self.__isFirstEntrance = False
                WWISE.WW_eventGlobal(Sounds.FIRST_SELECT_EVENT)
            else:
                WWISE.WW_eventGlobal(Sounds.SELECT_EVENT)
            if initialProgressionState is not None:
                WWISE.WW_setState(Sounds.PROGRESSION_STATE, initialProgressionState)
        else:
            WWISE.WW_eventGlobal(Sounds.DESELECT_EVENT)
        return

    def setCustomProgressSound(self, state):
        WWISE.WW_setState(Sounds.PROGRESSION_STATE, state)

    def setDefaultProgressSound(self):
        WWISE.WW_setState(Sounds.PROGRESSION_STATE, Sounds.PROGRESSION_STATE_DEFAULT)

    def setProgressSound(self, divisionUserID=None, isLoud=True):
        if isLoud:
            WWISE.WW_setState(Sounds.SUBVIEW_HANGAR_GENERAL, Sounds.SUBVIEW_HANGAR_GENERAL_OFF)
        else:
            WWISE.WW_setState(Sounds.SUBVIEW_HANGAR_GENERAL, Sounds.SUBVIEW_HANGAR_GENERAL_ON)
        if divisionUserID is None:
            WWISE.WW_setState(Sounds.PROGRESSION_STATE, Sounds.PROGRESSION_STATE_LEAGUES)
        else:
            stateSound = _DIVISION_TO_PROGRESSION_SOUND.get(divisionUserID)
            if stateSound is not None:
                WWISE.WW_setState(Sounds.PROGRESSION_STATE, stateSound)
        return

    def setAmbient(self, ambientType=AmbientType.NATURE):
        WWISE.WW_setState(Sounds.MAIN_PAGE_AMBIENT_STATE, _TYPE_TO_AMBIENT.get(ambientType))

    def setOverlayStateOn(self):
        WWISE.WW_setState(Sounds.OVERLAY_HANGAR_GENERAL, Sounds.OVERLAY_HANGAR_GENERAL_ON)
        WWISE.WW_setState(Sounds.OVERLAY_HANGAR_FILTERED, Sounds.OVERLAY_HANGAR_FILTERED_ON)

    def setOverlayStateOff(self):
        WWISE.WW_setState(Sounds.OVERLAY_HANGAR_FILTERED, Sounds.OVERLAY_HANGAR_FILTERED_OFF)
        WWISE.WW_setState(Sounds.OVERLAY_HANGAR_GENERAL, Sounds.OVERLAY_HANGAR_GENERAL_OFF)
