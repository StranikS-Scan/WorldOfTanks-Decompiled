# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/resource_well/constants.py
from enum import Enum
FEATURE = 'resource_well'

class LogActions(Enum):
    CLICK = 'click'
    CLOSE = 'close'
    OPEN = 'open'
    TOOLTIP_WATCHED = 'tooltip_watched'


class LogGroups(Enum):
    CHOOSE_SCREEN = 'choose_screen'
    COMPLETED_SCREEN = 'completed_screen'
    ENTRY_SCREEN = 'entry_screen'
    INFO_SCREEN = 'info_screen'
    INTRO_SCREEN = 'intro_screen'
    INTRO_VIDEO = 'intro_video'
    MAIN_SCREEN = 'main_screen'
    REFUND_TOOLTIP = 'refund_tooltip'
    SERIAL_NUMBER_TOOLTIP = 'serial_number_tooltip'
    VEHICLE_PREVIEW = 'vehicle_preview'


class ParentScreens(Enum):
    AWARD_SCREEN = 'award_screen'
    COMPLETED_SCREEN = 'completed_screen'
    INTRO_SCREEN = 'intro_screen'
    MAIN_SCREEN = 'main_screen'
    VEHICLE_PREVIEW = 'vehicle_preview'


class AdditionalInfo(Enum):
    BASIC_TAB = 'basic_tab'
    COMBAT_INTELLIGENCE = 'combat_intelligence'
    HANGAR_ENTRY_POINT = 'hangar_entry_point'
    NO_VEHICLES_NOTIFICATION_BUTTON = 'no_vehicles_notification_button'
    PARTICIPATION_FORBIDDEN = 'participation_forbidden'
    REFUND_AVAILABLE = 'refund_available'
    REFUND_UNAVAILABLE = 'refund_unavailable'
    SHOP_BANNER = 'shop_banner'
    START_NOTIFICATION_BUTTON = 'start_notification_button'
    STYLE_TAB = '3d_style_tab'
