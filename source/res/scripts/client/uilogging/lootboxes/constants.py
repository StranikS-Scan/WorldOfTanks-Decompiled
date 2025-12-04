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
    STATISTIC_OPEN_CLICK = 'statistic_open_click'
    STATISTIC_ESC_HOTKEY = 'statistic_esc_hotkey'
    STORAGE_ESC_HOTKEY = 'storage_esc_hotkey'


class Items(Enum):
    CAROUSEL_ENTRY_POINT = 'carousel_entry_point'
    ANIMATION_SWITCH_BUTTON = 'animation_switch_button'
    PROBABILITY_BTN = 'probability_btn'
    STATISTIC_BTN = 'statistic_btn'
    STATISTIC_NO_BOX_BTN = 'statistic_no_box_btn'
    STATISTIC_FULL_STATS_BTN = 'statistic_full_stats_btn'
    UNKNOWN_STATS_BTN = 'unknown_stats_btn'
    RIGHT_CORNER_BUY_BTN = 'right_corner_buy_btn'
    CURRENT_LOOTBOX_BUY_BTN = 'current_lootbox_buy_btn'
    NO_LOOTBOX_BUY_BTN = 'no_lootbox_buy_btn'
    UNKNOWN_BUY_BTN = 'unknown_buy_btn'
    CLOSE_CROSS_BTN = 'close_cross_btn'
    CLOSE_ESC_HOTKEY = 'close_esc_hotkey'
    CURRENT_LB_TAB = 'current_lootbox_tab'
    ALL_LB_TAB = 'all_boxes_tab'


class Views(Enum):
    HANGAR = 'hangar'
    STORAGE = 'storage'
    PROBABILITY = 'probability'
    REWARDS = 'rewards'
    REWARD_VIDEO = 'reward_video'
    WELCOME = 'welcome'
    STATISTICS_SHORT_STATS = 'statistics_short_stats'


BUY_BUTTONS_MAP = {0: Items.UNKNOWN_BUY_BTN,
 1: Items.RIGHT_CORNER_BUY_BTN,
 2: Items.CURRENT_LOOTBOX_BUY_BTN,
 3: Items.NO_LOOTBOX_BUY_BTN}
STATISTIC_BUTTONS_MAP = {0: Items.STATISTIC_BTN,
 1: Items.STATISTIC_NO_BOX_BTN,
 2: Items.STATISTIC_FULL_STATS_BTN,
 3: Items.UNKNOWN_STATS_BTN}
TABS_STATE_MAP = {0: Items.CURRENT_LB_TAB,
 1: Items.ALL_LB_TAB}
