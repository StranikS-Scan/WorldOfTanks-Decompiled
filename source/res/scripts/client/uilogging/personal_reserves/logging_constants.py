# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/personal_reserves/logging_constants.py
from enum import Enum
from typing import TYPE_CHECKING
from gui.impl.gen import R
if TYPE_CHECKING:
    from typing import Union
    DIALOG_LOGGING_ITEM_TYPES = Union[PersonalReservesLogDialogs, PersonalReservesLogButtons, str]
FEATURE = 'personal_reserves_20'
MIN_VIEW_TIME = 2.0
ACTIVATION_LAYOUT_ID = R.views.lobby.personal_reserves.ReservesActivationView()

class PersonalReservesLogActions(Enum):
    OPEN = 'open'
    CLOSE = 'close'
    CLICK = 'click'
    VIEWED = 'viewed'


class PersonalReservesLogKeys(Enum):
    HANGAR = 'hangar'
    LOBBY_HEADER = 'lobby_header_bar'
    ACTIVATION_WINDOW = 'reserves_activation_window'
    BATTLE = 'battle'
    INTRO_WINDOW = 'reserves_intro_window'
    RESERVES_CONVERSION_WINDOW = 'reserves_conversion_window'
    WIDGET = 'reserves_entry_point_widget'
    RESERVES_DEPOT_TAB = 'reserves_depot_tab'
    FULL_STATS_TAB = 'full_stats_tab'
    DEPOT = 'depo_storage_page'
    ACTIVATION_IN_BATTLE_TAB = 'in_battle_activation_tab'


class PersonalReservesLogNotifications(Enum):
    EXPIRE = 'reserve_expire_notification'


class PersonalReservesLogTooltips(Enum):
    RESERVES_WIDGET_TOOLTIP = 'reserves_widget_tooltip'


class PersonalReservesLogClicks(Enum):
    WIDGET_CLICKED = 'widget_clicked'


class PersonalReservesLogButtons(Enum):
    BUY_AND_ACTIVATE = 'buy_and_activate_button'
    BUY_GOLD = 'buy_gold_button'
    CANCEL = 'cancel_button'
    EXIT = 'exit_button'
    AFFIRMATIVE = 'affirmative_button'
    TO_RESERVES = 'to_reserves_button'
    GOTO_ACTIVATION = 'goto_activation_button'
    TAB_SELECT_BUTTON = 'tab_select_button'
    SHORTCUT_BUTTON = 'shortcut_button'


class PersonalReservesLogDialogs(Enum):
    BUY_AND_ACTIVATE = 'buy_and_activate_dialog'
    BUY_GOLD = 'buy_gold_dialog'
    BUY_AND_UPGRADE = 'buy_and_upgrade_dialog'


BATTLE_DURATION_KEY = 'battle_duration'
ARENA_PERIOD_KEY = 'arena_period'
SECONDS_SINCE_BATTLE_STARTED_KEY = 'seconds_since_battle_started'
ARENA_PERIOD_TO_KEY = {0: 'idle',
 1: 'waiting',
 2: 'prebattle',
 3: 'battle',
 4: 'afterbattle'}
