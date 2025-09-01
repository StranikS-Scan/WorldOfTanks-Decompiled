# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/sounds/sound_constants.py
from sound_gui_manager import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER
from white_tiger.cgf_components import wt_sound_helpers

class Sounds(CONST_CONTAINER):
    HANGAR_GROUP = 'STATE_hangar_place'
    HANGAR_STATE = 'STATE_hangar_place_garage'
    WT_HANGAR_ENTER = 'ev_white_tiger_hangar_enter'
    WT_HANGAR_EXIT = 'ev_white_tiger_hangar_exit'
    WT_HANGAR_AMBIENT_ENTER = 'ev_white_tiger_hangar_ambient'
    WT_HANGAR_AMBIENT_EXIT = 'ev_white_tiger_hangar_ambient_exit'
    STATE_GROUP_GAMEMODE = 'STATE_gamemode'
    STATE_GAMEMODE = 'STATE_gamemode_white_tiger'
    STATE_GAMEMODE_DEFAULT = 'STATE_gamemode_default'
    PROGRESSION_VIEW_ENTER = 'ev_white_tiger_hangar_collections_enter'
    PROGRESSION_VIEW_EXIT = 'ev_white_tiger_hangar_collections_exit'
    STATE_GROUP_PROGRESSION_PAGE = 'STATE_gamemode_progress_page'
    STATE_PROGRESSION_PAGE_ON = 'STATE_gamemode_progress_page_on'
    STATE_PROGRESSION_PAGE_OFF = 'STATE_gamemode_progress_page_off'
    INFO_PAGE_ENTER = 'ev_white_tiger_hangar_info_enter'
    INFO_PAGE_EXIT = 'ev_white_tiger_hangar_info_exit'
    REWARD_VIEW_GROUP = 'STATE_overlay_hangar_general'
    REWARD_VIEW_ENTER = 'STATE_overlay_hangar_general_on'
    REWARD_VIEW_EXIT = 'STATE_overlay_hangar_general_off'


WT_HANGAR_VIEW_SOUND_SPACE = CommonSoundSpaceSettings(name='white_tiger_hangar_view', entranceStates={Sounds.HANGAR_GROUP: Sounds.HANGAR_STATE}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
WT_PROGRESSION_VIEW_SOUND_SPACE = CommonSoundSpaceSettings(name='white_tiger_progression_view', entranceStates={Sounds.STATE_GROUP_PROGRESSION_PAGE: Sounds.STATE_PROGRESSION_PAGE_ON}, exitStates={Sounds.STATE_GROUP_PROGRESSION_PAGE: Sounds.STATE_PROGRESSION_PAGE_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=Sounds.PROGRESSION_VIEW_ENTER, exitEvent=Sounds.PROGRESSION_VIEW_EXIT)
WT_BATTLE_QUEUE_VIEW_SOUND_SPACE = CommonSoundSpaceSettings(name='white_tiger_battle_queue', entranceStates={Sounds.STATE_GROUP_PROGRESSION_PAGE: Sounds.STATE_PROGRESSION_PAGE_ON}, exitStates={Sounds.STATE_GROUP_PROGRESSION_PAGE: Sounds.STATE_PROGRESSION_PAGE_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
WT_REWARD_VIEW_SOUND_SPACE = CommonSoundSpaceSettings(name='white_tiger_reward_view', entranceStates={Sounds.REWARD_VIEW_GROUP: Sounds.REWARD_VIEW_ENTER}, exitStates={Sounds.REWARD_VIEW_GROUP: Sounds.REWARD_VIEW_EXIT}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')

def playInfoPageEnter():
    wt_sound_helpers.play2d(Sounds.INFO_PAGE_ENTER)


def playInfoPageExit():
    wt_sound_helpers.play2d(Sounds.INFO_PAGE_EXIT)


class WhiteTigerHangarSound(object):

    def __init__(self):
        self.__isActive = False

    def clear(self):
        self.isActive(False)

    def isActive(self, isActive=True):
        if self.__isActive != isActive:
            self.__isActive = isActive
            self.__setGamemodeState(isActive)
            self.__playSound(isActive)

    def __setGamemodeState(self, isActive=True):
        state = Sounds.STATE_GAMEMODE
        if not isActive:
            state = Sounds.STATE_GAMEMODE_DEFAULT
        wt_sound_helpers.setState(Sounds.STATE_GROUP_GAMEMODE, state)

    def __playSound(self, isActive=True):
        if isActive:
            wt_sound_helpers.play2d(Sounds.WT_HANGAR_ENTER)
            wt_sound_helpers.play2d(Sounds.WT_HANGAR_AMBIENT_ENTER)
        else:
            wt_sound_helpers.play2d(Sounds.WT_HANGAR_EXIT)
            wt_sound_helpers.play2d(Sounds.WT_HANGAR_AMBIENT_EXIT)
