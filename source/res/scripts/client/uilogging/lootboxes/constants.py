# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/lootboxes/constants.py
from enum import Enum
FEATURE = 'lootbox'
DEFAULT_TIME_LIMIT = 1.0

class Actions(Enum):
    OPEN = 'open'
    CLICK = 'click'
    TOOLTIP_WATCHED = 'tooltip_watched'
    ANIMATION_SWITCH = 'animation_switch'
    PROBABILITY_OPEN_CLICK = 'probability_open_click'
    PROBABILITY_VIEWED = 'probability_viewed'


class Items(Enum):
    CAROUSEL_ENTRY_POINT = 'carousel_entry_point'
    ANIMATION_SWITCH_BUTTON = 'animation_switch_button'
    PROBABILITY_BTN = 'probability_btn'
    RIGHT_CORNER_BUY_BTN = 'right_corner_buy_btn'
    CURRENT_LOOTBOX_BUY_BTN = 'current_lootbox_buy_btn'
    NO_LOOTBOX_BUY_BTN = 'no_lootbox_buy_btn'
    UNKNOWN_BUY_BTN = 'unknown_buy_btn'
    CLOSE_CROSS_BTN = 'close_cross_btn'
    CLOSE_ESC_HOTKEY = 'close_esc_hotkey'


class Views(Enum):
    HANGAR = 'hangar'
    STORAGE = 'storage'
    PROBABILITY = 'probability'
    REWARDS = 'rewards'
    REWARD_VIDEO = 'reward_video'
    WELCOME = 'welcome'


BUY_BUTTONS_MAP = {0: Items.UNKNOWN_BUY_BTN,
 1: Items.RIGHT_CORNER_BUY_BTN,
 2: Items.CURRENT_LOOTBOX_BUY_BTN,
 3: Items.NO_LOOTBOX_BUY_BTN}
