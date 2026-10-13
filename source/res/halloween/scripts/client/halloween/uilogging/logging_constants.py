# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/uilogging/logging_constants.py
from __future__ import absolute_import
from enum import Enum
FEATURE = 'hw26'
MIN_VIEW_TIME = 2.0
MIN_VO_TIME = 1

class HWLogActions(Enum):
    VO_LISTENED = 'vo_listened'
    TOOLTIP_VIEWED = 'tooltip_viewed'
    LIFETIME = 'lifetime'
    CLICK = 'click'
    OPEN = 'open'


class HWLogKeys(Enum):
    HW_LOBBY = 'hw_lobby'
    RANDOM_LOBBY = 'random_lobby'
    DECRYPT_VIEW = 'decrypt_view'
    REWARD_PATH_VIEW = 'reward_path_view'
    PROMO_VIEW = 'promo_view'
    EXCHANGE_VIEW = 'exchange_view'
    BESTIARY_VIEW = 'bestiary_view'
    MODE_SELECTOR_VIEW = 'mode_selector_view'
    COMPARISON_VIEW = 'comparison_view'
    ANOMALIES_VIEW = 'anomalies_view'
    HW_WEB_VIEW = 'hw_web_view'
    CAROUSEL = 'carousel'
    META_WIDGET = 'meta_widget'
    BATTLE_RESULT_STATS = 'battle_result_stats'
    BATTLE_RESULT_STATS_CM = 'battle_result_stats_cm'
    SIMPLE_TOOLTIP = 'simple_tooltip'
    HW_ENTRY_POINT = 'hw_entry_point'
    THUMBNAIL = 'thumbnail'
    ARROW = 'arrow'
    BUNDLE = 'bundle'
    INFO_BUTTON = 'info_button'
    BESTIARY_BUTTON = 'bestiary_button'
    COMPARISON_BUTTON = 'comparison_button'
    ANOMALIES_BUTTON = 'anomalies_button'
    VEHICLE_PREVIEW_BUTTON = 'vehicle_preview_button'
    VIEW_BUTTON = 'view_button'
    CONTEXT_MENU_BUTTON = 'context_menu_button'
    ADD_FRIEND_BUTTON = 'add_friend_button'
    SEND_PLATOON_INVITATION_BUTTON = 'send_platoon_invitation_button'
    SHOW_CONTEXT_MENU_BUTTON = 'show_context_menu_button'
    SKIP_BUTTON = 'skip_button'
    HANGAR_3D_OBJECT = '3d_object'
    UMG_BANNER = 'umg_banner'
    MODE_SELECTOR = 'mode_selector'
    HEADER = 'header'
    HW_HANGAR_UMG_WIDGET = 'hw_hangar_umg_widget'
    REWARD_PATH_UMG_WIDGET = 'reward_path_umg_widget'
