# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/veh_post_progression/constants.py
from enum import Enum
FEATURE = 'veh_post_progression'

class LogGroups(Enum):
    ADD_TO_COMPARE = 'add_to_compare'
    COMPARE_MODIFICATIONS_TREE = 'compare_modifications_tree'
    CONFIRM_BUTTON = 'confirm_button'
    CUSTOM_SLOT_SPECIALIZATION = 'custom_slot_specialization'
    ENTRY_POINT = 'entry_point'
    FEATURE_MODIFICATION = 'feature_modification'
    INFO_BUTTON = 'info_button'
    MODIFICATION_LEVEL = 'modification_level'
    PAIR_MODIFICATION = 'pair_modification'
    ROLES_FILTER = 'roles_filter'
    SWITCH_PANEL = 'switch_panel'


class LogActions(Enum):
    CLICK = 'click'
    CONTEXT_MENU = 'context_menu'
    CLOSE = 'close'
    HOTKEY = 'hotkey'
    TOOLTIP_WATCHED = 'tooltip_watched'


class LogAdditionalInfo(Enum):
    LOCKED = 'locked'
    UNLOCKED = 'unlocked'


class ParentScreens(Enum):
    COMPARE_MODIFICATIONS_TREE = 'compare_modifications_tree'
    HANGAR = 'hangar'
    HUD = 'hud'
    MODIFICATIONS_TREE = 'modifications_tree'
    RESEARCH_PAGE = 'research_page'
    ROLE_SLOT_SELECTION_DIALOG = 'role_slot_selection_dialog'
    TANK_SETUP = 'tank_setup'
    VEH_COMPARE = 'veh_compare'
