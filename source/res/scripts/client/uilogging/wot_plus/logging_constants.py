# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/wot_plus/logging_constants.py
from collections import namedtuple
from enum import Enum
InfoPageInfo = namedtuple('InfoPageInfo', 'item, parent_screen')
FEATURE = 'wot_plus'
MIN_VIEW_TIME = 2.0

class WotPlusLogActions(Enum):
    CLOSE = 'close'
    CLICK = 'click'
    VIEWED = 'viewed'


class WotPlusKeys(Enum):
    HANGAR = 'hangar'
    REWARD_SCREEN = 'reward_screen'
    RESERVE_VIEW = 'reserve_view'
    RESERVE_AWARD_VIEW = 'reserve_award_view'
    HEADER_TOOLTIP = 'header_tooltip'
    CLOSE_BUTTON = 'close_button'


class RewardScreenTooltips(Enum):
    EXCLUSIVE_VEHICLE = 'exclusive_vehicle_tooltip'
    GOLD_RESERVE = 'gold_reserve_tooltip'
    PASSIVE_CREW_XP = 'passive_crew_xp_tooltip'
    EXCLUDED_MAP = 'excluded_map_tooltip'
    FREE_EQUIPMENT_MOVEMENT = 'free_equipment_movement_tooltip'


class ReservesKeys(Enum):
    ACTIVATE_WP = 'activate_wp_button'
    ACTIVATE_PA = 'activate_pa_button'
    INFO_TOOLTIP = 'info_tooltip'
    WP_INFO = 'wp_info_button'
    PA_INFO = 'pa_info_button'


class HeaderItemState(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'


class WotPlusInfoPageSource(Enum):
    SHOP = InfoPageInfo('card_details_button', 'shop')
    REWARD_SCREEN = InfoPageInfo('details_button', WotPlusKeys.REWARD_SCREEN)
    SUBSCRIPTION_PAGE = InfoPageInfo('info_button', 'subscription_page')
    GOLD_RESERVES = InfoPageInfo('info_button', WotPlusKeys.RESERVE_VIEW)
