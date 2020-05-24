# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/statistic/logging_constants.py
from bootcamp.BootcampConstants import HINT_TYPE
__all__ = ('BC_LOG_KEYS', 'CHECK', 'BATTLE_HINTS_TO_LOG_ON_COMPLETE', 'BATTLE_HINTS_TO_LOG_ON_HIDE', 'HANGAR_HINTS_TO_LOG_ON_COMPLETE')

class BC_LOG_ACTIONS:
    SKIP_VIDEO = 'skip_video'
    MOUSE_CLICK = 'mouse_click'
    MOUSE_MOVE = 'mouse_move'
    CLOSE = 'close'
    CONTINUE_BUTTON_PRESSED = 'continue_button_pressed'
    RESEARCH_BUTTON_PRESSED = 'research_button_pressed'
    BATTLE_BUTTON_PRESSED = 'battle_button_pressed'
    BUY_ITEM = 'buy_item'
    UNLOCK_ITEM = 'unlock_item'


class SNIPER_MODE:
    ON = 'sniper_mode_on'
    OFF = 'sniper_mode_off'


BATTLE_HINTS_TO_LOG_ON_COMPLETE = {HINT_TYPE.HINT_MOVE_TURRET: 'move_turret',
 HINT_TYPE.HINT_MOVE: 'move',
 HINT_TYPE.HINT_SHOOT: 'shoot'}
BATTLE_HINTS_TO_LOG_ON_HIDE = {HINT_TYPE.HINT_AIM: 'aim',
 HINT_TYPE.HINT_MESSAGE_AVOID: 'avoid_enemy',
 HINT_TYPE.HINT_B3_FALL_BACK: 'fall_back',
 HINT_TYPE.HINT_B3_FLANK: 'flank',
 HINT_TYPE.HINT_REPAIR_TRACK: 'repair_track',
 HINT_TYPE.HINT_HEAL_CREW: 'heal_crew',
 HINT_TYPE.HINT_USE_EXTINGUISHER: 'use_extinguisher',
 HINT_TYPE.HINT_WEAK_POINTS: 'weak_points'}
BATTLE_HINTS_TO_LOG_ON_ANIMATION_FINISH = {HINT_TYPE.HINT_SNIPER_ON_DISTANCE: SNIPER_MODE.ON,
 HINT_TYPE.HINT_SNIPER: SNIPER_MODE.ON}
SNIPER_MODE_SEQUENCE = [SNIPER_MODE.ON, SNIPER_MODE.OFF]
ACTION_SEQUENCES = {SNIPER_MODE.ON: SNIPER_MODE_SEQUENCE}
HANGAR_HINTS_TO_LOG_ON_COMPLETE = {22: BC_LOG_ACTIONS.MOUSE_MOVE}
ACTIONS_HINTS_TO_LOG_ONCE = [BC_LOG_ACTIONS.UNLOCK_ITEM,
 BC_LOG_ACTIONS.BUY_ITEM,
 BC_LOG_ACTIONS.RESEARCH_BUTTON_PRESSED,
 BATTLE_HINTS_TO_LOG_ON_HIDE[HINT_TYPE.HINT_WEAK_POINTS]]
HANGAR_MENU_ITEMS = {'hangar': 'hangar',
 'techtree': 'techtree'}
BC_AWARDS_MAP = {'1': 'medal_block',
 '0': 'rewards_block',
 '': 'XP/credits block',
 'blocked': 'blocked',
 'damage': 'damage',
 'destroyed': 'destroyed',
 'detected': 'detected',
 'assisted': 'assisted'}

class BC_LOG_KEYS:
    BC_NATION_SELECT = 'bc_nation_select'
    BC_BATTLE_HINTS = 'bc_battle_hints'
    BC_INTRO_VIDEO = 'bc_intro_video'
    BC_OUTRO_VIDEO = 'bc_outro_video'
    BC_INTERLUDE_VIDEO = 'bc_interlude_video'
    BC_RESULT_SCREEN = 'bc_result_screen'
    BC_HANGAR_HINTS = 'bc_hangar_hints'
    BC_RESEARCH_VEHICLES = 'bc_research_vehicles'
    BC_HANGAR_MENU = 'bc_hangar_menu'
    BC_PERSONAL_CASE = 'bc_personal_case'


class CHECK:
    GREATER_THAN = 'gt'
    EQUAL = 'eq'


class LIMITS:
    INVALID_MIN_LENGTH = 0
    INTRO_VIDEO_MAX_LENGTH = 50
