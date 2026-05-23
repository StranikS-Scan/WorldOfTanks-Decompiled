# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/fun_gui_constants.py
from __future__ import absolute_import
from constants_utils import ConstInjector
from gui.limited_ui.lui_rules_storage import LUI_RULES
from gui.prb_control import settings
from gui.shared.gui_items import Vehicle
from messenger import m_constants
from shared_utils import CONST_CONTAINER
ATTR_NAME = 'FUN_RANDOM'
PRB_REQ_TYPE_ATTR_NAME = 'CHANGE_FUN_SUB_MODE'
_LUI_RULE_ENTRY_POINT = 'FunRandomEntryPoint'
_LUI_RULE_NOTIFICATIONS = 'FunRandomNotifications'
_LUI_RULES = [_LUI_RULE_ENTRY_POINT, _LUI_RULE_NOTIFICATIONS]

class FUNCTIONAL_FLAG(settings.FUNCTIONAL_FLAG, ConstInjector):
    FUN_RANDOM = 268435456


class PREBATTLE_ACTION_NAME(settings.PREBATTLE_ACTION_NAME, ConstInjector):
    _const_type = str
    FUN_RANDOM = 'fun_random'
    FUN_RANDOM_SQUAD = 'funRandomSquad'


class SELECTOR_BATTLE_TYPES(settings.SELECTOR_BATTLE_TYPES, ConstInjector):
    _const_type = str
    FUN_RANDOM = 'funRandom'


class REQUEST_TYPE(settings.REQUEST_TYPE, ConstInjector):
    CHANGE_FUN_SUB_MODE = 47


class SCH_CLIENT_MSG_TYPE(m_constants.SCH_CLIENT_MSG_TYPE, ConstInjector):
    FUN_RANDOM_NOTIFICATIONS = 100
    FUN_RANDOM_PROGRESSION = 101


class VEHICLE_TAGS(Vehicle.VEHICLE_TAGS, ConstInjector):
    _const_type = str
    FUN_RANDOM = 'fun_random'


class FunRandomTooltipConstants(CONST_CONTAINER):
    FUN_RANDOM_CALENDAR_DAY = 'funRandomCalendarDay'
    FUN_RANDOM_MODE_SELECTOR_CALENDAR_DAY = 'funRandomModeSelectorCalendarDay'
    FUN_RANDOM_REWARDS = 'funRandomRewards'
    LOBBY_TOOLTIPS_SET = (FUN_RANDOM_CALENDAR_DAY, FUN_RANDOM_MODE_SELECTOR_CALENDAR_DAY, FUN_RANDOM_REWARDS)


class AccountSettingsConstants(CONST_CONTAINER):
    FUN_RANDOM_ACCOUNT_SETTINGS = 'funRandomAccountSettings'
    FUN_RANDOM_INFO_PAGE_SHOWN = 'funRandomInfoPageShown'
    FUN_RANDOM_SEEN_TRIGGERS_COMPLETION = 'funRandomSeenTriggersCompletion'


ACCOUNT_SUBMODE_DEFAULT_SETTINGS = {AccountSettingsConstants.FUN_RANDOM_INFO_PAGE_SHOWN: False}

def initFunRandomLimitedUIIds():
    LUI_RULES.inject(_LUI_RULES)
