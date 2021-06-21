# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/veh_post_progression/constants.py
from enum import Enum
FEATURE = 'veh_post_progression'

class LogGroups(Enum):
    ADD_TO_COMPARE = 'add_to_compare'
    CANCEL_BUTTON = 'cancel_button'
    CUSTOM_SLOT_SPECIALIZATION = 'custom_slot_specialization'
    ENTRY_POINT = 'entry_point'
    FEATURE_MODIFICATION = 'feature_modification'
    INFO_BUTTON = 'info_button'
    MODIFICATION_LEVEL = 'modification_level'
    SWITCH_PANEL = 'switch_panel'
    PAIR_MODIFICATION = 'pair_modification'


class LogActions(Enum):
    CLICK = 'click'
    CONTEXT_MENU = 'context_menu'
    CLOSE = 'close'
    HOTKEY = 'hotkey'
    TOOLTIP_WATCHED = 'tooltip_watched'


class LogAdditionalInfo(Enum):
    DESTROY_MODIFICATION = 'destroy_modification'
    LOCKED = 'locked'
    MODIFICATION_LEVEL = 'modification_level'
    PAIR_MODIFICATION = 'pair_modification'
    UNLOCKED = 'unlocked'


class ParentScreens(Enum):
    CONFIRMATION_DIALOG = 'confirmation_dialog'
    HANGAR = 'hangar'
    HUD = 'hud'
    MODIFICATIONS_TREE = 'modifications_tree'
    RESEARCH_PAGE = 'research_page'
    TANK_SETUP = 'tank_setup'


class EntryPointCallers(Enum):
    CONTEXT_MENU = 'context_menu'
    HANGAR = 'hangar'
    RESEARCH_PAGE = 'research_page'
