# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/fun_sounds.py
from sound_gui_manager import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class FunSounds(CONST_CONTAINER):
    HANGAR_PLACE_STATE = 'STATE_hangar_place'
    HANGAR_PLACE_TASKS = 'STATE_hangar_place_fep'
    OVERLAY_HANGAR_STATE = 'STATE_overlay_hangar_general'
    OVERLAY_HANGAR_STATE_ON = 'STATE_overlay_hangar_general_on'
    OVERLAY_HANGAR_STATE_OFF = 'STATE_overlay_hangar_general_off'
    PROGRESSION_SPACE_NAME = 'fun_progression_view'
    PROGRESSION_ENTER_EVENT = 'ev_fep_meta_enter'
    PROGRESSION_EXIT_EVENT = 'ev_fep_meta_exit'
    REWARDS_SPACE_NAME = 'fun_rewards_view'
    REWARDS_SCREEN_GENERAL = 'gui_reward_screen_general'
    TIER_LIST_SPACE_NAME = 'fun_tier_list'
    TIER_LIST_ENTER = 'ev_fep_infopage_enter'
    TIER_LIST_EXIT = 'ev_fep_infopage_exit'
    BATTLE_RESULTS_SPACE_NAME = 'fun_postbattle_view'
    GAMEPLACE_STATE = 'STATE_gameplace'
    GAMEPLACE_BATTLE_RESULTS_STATE = 'STATE_gameplace_result'
    GAMEPLACE_HANGAR_STATE = 'STATE_gameplace_hangar'
    BATTLE_RESULTS_ENTER_EVENT = 'gui_hangar_neutral_screen'


FUN_PROGRESSION_SOUND_SPACE = CommonSoundSpaceSettings(name=FunSounds.PROGRESSION_SPACE_NAME, entranceStates={FunSounds.HANGAR_PLACE_STATE: FunSounds.HANGAR_PLACE_TASKS}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=FunSounds.PROGRESSION_ENTER_EVENT, exitEvent=FunSounds.PROGRESSION_EXIT_EVENT)
FUN_REWARD_SCREEN_SOUND_SPACE = CommonSoundSpaceSettings(name=FunSounds.REWARDS_SPACE_NAME, entranceStates={FunSounds.OVERLAY_HANGAR_STATE: FunSounds.OVERLAY_HANGAR_STATE_ON}, exitStates={FunSounds.OVERLAY_HANGAR_STATE: FunSounds.OVERLAY_HANGAR_STATE_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=FunSounds.REWARDS_SCREEN_GENERAL, exitEvent='')
FUN_TIER_LIST_SOUND_SPACE = CommonSoundSpaceSettings(name=FunSounds.TIER_LIST_SPACE_NAME, entranceStates={}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=FunSounds.TIER_LIST_ENTER, exitEvent=FunSounds.TIER_LIST_EXIT)
FUN_BATTLE_RESULTS_SOUND_SPACE = CommonSoundSpaceSettings(name=FunSounds.BATTLE_RESULTS_SPACE_NAME, entranceStates={FunSounds.GAMEPLACE_STATE: FunSounds.GAMEPLACE_BATTLE_RESULTS_STATE}, exitStates={FunSounds.GAMEPLACE_STATE: FunSounds.GAMEPLACE_HANGAR_STATE}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=FunSounds.BATTLE_RESULTS_ENTER_EVENT, exitEvent='')
