# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_helpers/sound_manager.py
import WWISE
from gui.Scaleform.framework.entities.View import CommonSoundSpaceSettings
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from shared_utils import CONST_CONTAINER

class Sounds(CONST_CONTAINER):
    FIRST_SELECT_EVENT = 'gui_rb_rank_Entrance_first'
    SELECT_EVENT = 'gui_rb_rank_Entrance'
    DESELECT_EVENT = 'gui_rb_rank_Exit'
    OVERLAY_SPACE_NAME = 'ranked_overlay'
    OVERLAY_HANGAR_GENERAL = 'STATE_overlay_hangar_general'
    OVERLAY_HANGAR_GENERAL_ON = 'STATE_overlay_hangar_general_on'
    OVERLAY_HANGAR_GENERAL_OFF = 'STATE_overlay_hangar_general_off'
    MAIN_PAGE_SPACE_NAME = 'ranked_main_page'
    MAIN_PAGE_STATE = 'STATE_gamemode_progress_page'
    MAIN_PAGE_STATE_ON = 'STATE_gamemode_progress_page_on'
    MAIN_PAGE_STATE_OFF = 'STATE_gamemode_progress_page_off'
    PROGRESSION_STATE = 'STATE_rank_level'
    PROGRESSION_STATE_DEFAULT = 'STATE_rank_level_00'
    PROGRESSION_STATE_QUALIFICATION = 'STATE_rank_level_01'
    PROGRESSION_STATE_3_DIVISION = 'STATE_rank_level_02'
    PROGRESSION_STATE_2_DIVISION = 'STATE_rank_level_03'
    PROGRESSION_STATE_1_DIVISION = 'STATE_rank_level_04'
    PROGRESSION_STATE_LEAGUES = 'STATE_rank_level_05'


RANKED_MAIN_PAGE_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.MAIN_PAGE_SPACE_NAME, entranceStates={Sounds.MAIN_PAGE_STATE: Sounds.MAIN_PAGE_STATE_ON}, exitStates={Sounds.MAIN_PAGE_STATE: Sounds.MAIN_PAGE_STATE_OFF,
 Sounds.OVERLAY_HANGAR_GENERAL: Sounds.OVERLAY_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
RANKED_OVERLAY_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.OVERLAY_SPACE_NAME, entranceStates={Sounds.OVERLAY_HANGAR_GENERAL: Sounds.OVERLAY_HANGAR_GENERAL_ON}, exitStates={Sounds.OVERLAY_HANGAR_GENERAL: Sounds.OVERLAY_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
_DIVISION_TO_PROGRESSION_SOUND = {RANKEDBATTLES_ALIASES.DIVISIONS_CLASSIFICATION: Sounds.PROGRESSION_STATE_QUALIFICATION,
 RANKEDBATTLES_ALIASES.DIVISIONS_BRONZE: Sounds.PROGRESSION_STATE_3_DIVISION,
 RANKEDBATTLES_ALIASES.DIVISIONS_SILVER: Sounds.PROGRESSION_STATE_2_DIVISION,
 RANKEDBATTLES_ALIASES.DIVISIONS_GOLD: Sounds.PROGRESSION_STATE_1_DIVISION}

class RankedSoundManager(object):
    __isFirstEntrance = True

    def __init__(self):
        self.__isFirstEntrance = True

    @staticmethod
    def setDefaultProgressSound():
        WWISE.WW_setState(Sounds.PROGRESSION_STATE, Sounds.PROGRESSION_STATE_DEFAULT)

    @staticmethod
    def setProgressSound(divisionUserID=None, isLoud=True):
        if isLoud:
            WWISE.WW_setState(Sounds.OVERLAY_HANGAR_GENERAL, Sounds.OVERLAY_HANGAR_GENERAL_OFF)
        else:
            WWISE.WW_setState(Sounds.OVERLAY_HANGAR_GENERAL, Sounds.OVERLAY_HANGAR_GENERAL_ON)
        if divisionUserID is None:
            WWISE.WW_setState(Sounds.PROGRESSION_STATE, Sounds.PROGRESSION_STATE_LEAGUES)
        else:
            stateSound = _DIVISION_TO_PROGRESSION_SOUND.get(divisionUserID)
            if stateSound is not None:
                WWISE.WW_setState(Sounds.PROGRESSION_STATE, stateSound)
        return

    def clear(self):
        self.__isFirstEntrance = True

    def onPrbEntityChange(self, isRankedPrbSelected, isMastered):
        if isRankedPrbSelected:
            if self.__isFirstEntrance:
                self.__isFirstEntrance = False
                WWISE.WW_eventGlobal(Sounds.FIRST_SELECT_EVENT)
            else:
                WWISE.WW_eventGlobal(Sounds.SELECT_EVENT)
            if isMastered:
                WWISE.WW_setState(Sounds.PROGRESSION_STATE, Sounds.PROGRESSION_STATE_LEAGUES)
            else:
                WWISE.WW_setState(Sounds.PROGRESSION_STATE, Sounds.PROGRESSION_STATE_DEFAULT)
        else:
            WWISE.WW_eventGlobal(Sounds.DESELECT_EVENT)
