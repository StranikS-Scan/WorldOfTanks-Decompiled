# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/sounds.py
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings

class RandomBattleResultsSounds(CONST_CONTAINER):
    BATTLE_RESULTS_SPACE_NAME = 'postbattle_view'
    GAMEPLACE_STATE = 'STATE_gameplace'
    GAMEPLACE_BATTLE_RESULTS_STATE = 'STATE_gameplace_result'
    GAMEPLACE_HANGAR_STATE = 'STATE_gameplace_hangar'
    OVERLAY_HANGAR_FILTERED = 'STATE_hangar_filtered'
    OVERLAY_HANGAR_FILTERED_ON = 'STATE_hangar_filtered_on'
    OVERLAY_HANGAR_FILTERED_OFF = 'STATE_hangar_filtered_off'


RANDOM_BATTLE_RESULTS_SOUND_SPACE = CommonSoundSpaceSettings(name=RandomBattleResultsSounds.BATTLE_RESULTS_SPACE_NAME, entranceStates={RandomBattleResultsSounds.GAMEPLACE_STATE: RandomBattleResultsSounds.GAMEPLACE_BATTLE_RESULTS_STATE,
 RandomBattleResultsSounds.OVERLAY_HANGAR_FILTERED: RandomBattleResultsSounds.OVERLAY_HANGAR_FILTERED_ON}, exitStates={RandomBattleResultsSounds.GAMEPLACE_STATE: RandomBattleResultsSounds.GAMEPLACE_HANGAR_STATE,
 RandomBattleResultsSounds.OVERLAY_HANGAR_FILTERED: RandomBattleResultsSounds.OVERLAY_HANGAR_FILTERED_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
