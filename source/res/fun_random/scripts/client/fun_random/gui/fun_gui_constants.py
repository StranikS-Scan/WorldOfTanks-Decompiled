# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/fun_gui_constants.py
from constants_utils import ConstInjector
from gui.limited_ui.lui_rules_storage import LUI_RULES
from gui.prb_control import settings
from messenger import m_constants
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


def initFunRandomLimitedUIIds():
    LUI_RULES.inject(_LUI_RULES)
