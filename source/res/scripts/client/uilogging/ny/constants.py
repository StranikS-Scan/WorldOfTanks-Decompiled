# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/ny/constants.py
from enum import Enum
FEATURE = 'ny2022_event'

class LogGroups(Enum):
    BRO_ICON = 'bro_icon'
    CELEBRITY_BUTTON = 'celebrity_button'
    CONTEXT_MENU = 'context_menu'
    FLOW = 'flow'
    INFO_VIDEO = 'info_video'
    INTRO_PAGE = 'intro_page'
    NY_INFO_PAGE = 'ny_info_page'
    NY_MAIN_WIDGET = 'ny_main_widget'
    NY_SELECTABLE_OBJECT = 'ny_selectable_object'
    SEND_BUTTON = 'send_button'
    STAMP_ICON = 'stamp_icon'
    STATISTICS_BUTTON = 'statistics_button'
    WIDGET_TOP_MENU_TAB = 'widget_top_menu_tab'


class LogActions(Enum):
    CLICK = 'click'
    CLOSE = 'close'
    MOVE = 'move'
    TOOLTIP_WATCHED = 'tooltip_watched'


class AdditionalInfo(Enum):
    CELEBRITY = 'celebrity'
    INFO_ENTRY_POINT = 'info_entry_point'
    GIFT_SYSTEM_ENTRY_POINT = 'gift_system_entry_point'
    MESSAGE_CHANGED = 'message_changed'
    MULTI_OPEN = 'multiple_open'
    TREE = 'tree'
    SINGLE_OPEN = 'single_open'
    VEHICLES = 'vehicles'


class ParentScreens(Enum):
    BATTLE_QUESTS_PAGE = 'battle_quests_page'
    GIFT_SYSTEM_PAGE = 'gift_system_page'
    HANGAR = 'hangar'
    NY_BOXES_PAGE = 'ny_boxes_page'
    NY_LOBBY = 'ny_lobby'
    NY_INFO_PAGE = 'ny_info_page'
    REWARDS_PAGE = 'rewards_page'


class Views(Enum):
    ALBUMS = 'albums_'
    BIG_DECORATIONS = 'big_decorations'
    CELEBRITY = 'celebrity'
    COLLIDER = 'collider'
    GIFT_SYSTEM = 'gift_system'
    HANGAR = 'hangar'
    INFO = 'info_page'
    INSTALLATION = 'installation'
    KITCHEN = 'kitchen'
    LOOTBOXES = 'lootboxes'
    LOOTBOX_STYLE_PREVIEW = 'lootbox_style_preview'
    REWARDS_FOR_LEVELS = 'rewards_for_levels'
    REWARDS = 'rewards_'
    SHARDS = 'shards'
    TREE = 'tree'
    VEHICLES = 'vehicles'


class TransitionMethods(Enum):
    ALBUM_DECORATIONS_SLOT = 'album_decorations_slot'
    ALBUM_REWARDS_BUTTON = 'album_rewards_button'
    BIG_DECORATIONS_SLOT_POPOVER = 'big_decorations_slot_popover'
    CLOSE_BUTTON = 'close_button'
    CURRENT_YEAR_ALBUM_BUTTON = 'current_year_album_button'
    ESC_BUTTON = 'esc_button'
    FIGHT_BUTTON = 'fight_button'
    GIFT_SYSTEM_CELEBRITY_BUTTON = 'gift_system_celebrity_button'
    INFO_ENTRY_POINT = 'info_entry_point'
    INFO_BACK_BUTTON = 'info_back_button'
    INFO_PAGE_BUTTON = 'info_page_buttons'
    LOBBY_HEADER = 'lobby_header'
    LOOTBOXES_CELEBRITY_BUTTON = 'lootboxes_celebrity_button'
    LOOTBOXES_CLOSE_BUTTON = 'lootboxes_close_button'
    LOOTBOXES_PAGE_BUTTONS = 'lootboxes_page_buttons'
    LOOTBOXES_POPOVER_OPEN = 'lootboxes_popover_open'
    LOOTBOXES_POPOVER_BUY = 'lootboxes_popover_buy'
    NY_MAIN_WIDGET = 'ny_main_widget'
    PREVIEW_BACK_BUTTON = 'preview_back_button'
    REWARDS_ALBUM_BUTTON = 'rewards_album_button'
    SELECTABLE_OBJECT = '3d_selectable_object'
    SHOW_LOOTBOX_VEHICLE = 'show_lootbox_vehicle'
    SHOW_LOOTBOX_STYLE_PREVIEW = 'show_lootbox_style_preview'
    SIDE_BAR_TAB = 'side_bar_tab'
    SMALL_DECORATIONS_SLOT_POPOVER = 'small_decorations_slot_popover'
    VEHICLES_INFO_BUTTON = 'vehicles_info_button'
    WIDGET_TOP_MENU_TAB = 'widget_top_menu_tab'
