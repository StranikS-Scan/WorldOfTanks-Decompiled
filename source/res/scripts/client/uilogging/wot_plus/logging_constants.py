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
    DETAILS_BUTTON = 'details_button'
    INFO_BUTTON = 'info_button'
    NOTIFICATION_CENTER = 'notification_center'
    ATTENDANCE_REWARD_SCREEN = 'attendance_reward_screen'
    ACCOUNT_DASHBOARD = 'account_dashboard'
    SUBSCRIPTION_PAGE = 'subscription_page'


class RewardScreenTooltips(Enum):
    EXCLUSIVE_VEHICLE = 'exclusive_vehicle_tooltip'
    GOLD_RESERVE = 'gold_reserve_tooltip'
    PASSIVE_CREW_XP = 'passive_crew_xp_tooltip'
    EXCLUDED_MAP = 'excluded_map_tooltip'
    FREE_EQUIPMENT_MOVEMENT = 'free_equipment_movement_tooltip'
    ATTENDANCE_REWARD = 'attendance_reward_tooltip'


class ReservesKeys(Enum):
    GOLD_ACTIVATE = 'activate_wp_button'
    CREDITS_ACTIVATE = 'activate_pa_button'
    INFO_TOOLTIP = 'info_tooltip'
    GOLD_INFO = 'wp_info_button'
    CREDITS_INFO = 'pa_info_button'


class WotPlusStateStr(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'


class PremiumAccountStateStr(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'


class HeaderAdditionalData(Enum):
    NEW_ATTENDANCE_REWARD = 'new'


class NotificationAdditionalData(Enum):
    RELEASE_NOTIFICATION = 'release_notification'
    SPECIAL_NOTIFICATION = 'special_notification'


class WotPlusInfoPageSource(Enum):
    SHOP = InfoPageInfo('card_details_button', 'shop')
    REWARD_SCREEN = InfoPageInfo(WotPlusKeys.DETAILS_BUTTON, WotPlusKeys.REWARD_SCREEN)
    SUBSCRIPTION_PAGE = InfoPageInfo(WotPlusKeys.INFO_BUTTON, WotPlusKeys.SUBSCRIPTION_PAGE)
    GOLD_RESERVES = InfoPageInfo(ReservesKeys.GOLD_INFO, WotPlusKeys.RESERVE_VIEW)
    ATTENDANCE_REWARDS_SCREEN = InfoPageInfo(WotPlusKeys.INFO_BUTTON, WotPlusKeys.ATTENDANCE_REWARD_SCREEN)


class AccountDashboardFeature(Enum):
    SUBSCRIPTION_WIDGET = 'subscription_widget'
    RESERVE_WIDGET = 'reserve_widget'
    EXCLUDED_MAPS_WIDGET = 'excluded_maps_widget'


class SubscriptionPageKeys(Enum):
    INFO_BUTTON = WotPlusKeys.INFO_BUTTON
    CTA_BUTTON = 'cta_button'


class SubscriptionStateMixinKeys(Enum):
    WOT_PLUS = 'wotp'
    PREMIUM = 'pa'
