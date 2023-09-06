# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/common/story_mode_common/battle_mode.py
from constants_utils import AbstractBattleMode
from story_mode_common.battle_results import story_mode
from story_mode_constants import PREBATTLE_TYPE, QUEUE_TYPE, ARENA_GUI_TYPE, ARENA_BONUS_TYPE, STORY_MODE_GAME_PARAMS_KEY, SM_CONGRATULATIONS_MESSAGE

class StoryModeBattleMode(AbstractBattleMode):
    _PREBATTLE_TYPE = PREBATTLE_TYPE.STORY_MODE
    _QUEUE_TYPE = QUEUE_TYPE.STORY_MODE
    _ARENA_BONUS_TYPE = ARENA_BONUS_TYPE.STORY_MODE
    _ARENA_GUI_TYPE = ARENA_GUI_TYPE.STORY_MODE
    _BATTLE_MGR_NAME = 'StoryModeBattlesMgr'
    _GAME_PARAMS_KEY = STORY_MODE_GAME_PARAMS_KEY
    _BATTLE_RESULTS_CONFIG = story_mode
    _SM_TYPE_BATTLE_RESULT = 'storyModeBattleResults'
    _SM_TYPES = [_SM_TYPE_BATTLE_RESULT, SM_CONGRATULATIONS_MESSAGE]
