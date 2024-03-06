# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/newbie_hints/constants.py
from enum import Enum
from account_helpers.settings_core.options import AimSetting
from account_helpers.settings_core import settings_constants
FEATURE_NEWBIE_HINTS = 'newbie_hints'
FEATURE_NEWBIE_HINTS_SETTINGS = 'newbie_hints_settings'
TOOLTIP_MIN_VIEW_TIME = 2.0

class NewbieHintsLogActions(str, Enum):
    APPLY = 'apply'
    WATCHED = 'watched'
    CLICK = 'click'


class NewbieHintsLogViews(str, Enum):
    SETTINGS = 'settings'
    SETTINGS_ARCADE = 'settings_arcade'
    SETTINGS_SNIPER = 'settings_sniper'
    BATTLE = 'battle'


class SettingsNewbieTooltips(str, Enum):
    PREBATTLE_HINTS = '#tooltips:newbiePrebattleHints'
    INBATTLE_HINTS = '#tooltips:newbieBattleHints'
    INBATTLE_HINTS_RESET = 'restartNewbieBattleHints'


class CheckBoxState(str, Enum):
    ENABLE = 'enable'
    DISABLE = 'disable'


class NewbieHintsLogItems(str, Enum):
    BTN_RESET_VIEWED_HINTS = 'inbattle_hints_reset_btn'
    CHECKBOX_PREBATTLE_HINTS = 'prebattle_hints_checkbox'
    CHECKBOX_INBATTLE_HINTS = 'inbattle_hints_checkbox'
    TOOLTIP_SETTINGS_PREBATTLE_HINTS = 'prebattle_hints_tooltip'
    TOOLTIP_SETTINGS_INBATTLE_HINTS = 'inbattle_hints_tooltip'
    TOOLTIP_SETTINGS_INBATTLE_HINTS_RESET = 'inbattle_reset_tooltip'


SETTINGS_CHECKBOX_KEYS_MAPPING = {settings_constants.GAME.NEWBIE_PREBATTLE_HINTS: NewbieHintsLogItems.CHECKBOX_PREBATTLE_HINTS,
 settings_constants.GAME.NEWBIE_BATTLE_HINTS: NewbieHintsLogItems.CHECKBOX_INBATTLE_HINTS}
TOOLTIP_ID_MAPPING = {SettingsNewbieTooltips.PREBATTLE_HINTS: NewbieHintsLogItems.TOOLTIP_SETTINGS_PREBATTLE_HINTS,
 SettingsNewbieTooltips.INBATTLE_HINTS: NewbieHintsLogItems.TOOLTIP_SETTINGS_INBATTLE_HINTS,
 SettingsNewbieTooltips.INBATTLE_HINTS_RESET: NewbieHintsLogItems.TOOLTIP_SETTINGS_INBATTLE_HINTS_RESET}
NEWBIE_HINTS_RETICLE_MAPPING = {settings_constants.AIM.ARCADE: NewbieHintsLogViews.SETTINGS_ARCADE,
 settings_constants.AIM.SNIPER: NewbieHintsLogViews.SETTINGS_SNIPER}
NEWBIE_SETTINGS_RETICLE_PARAMS = [AimSetting.OPTIONS.GUN_TAG_TYPE]
