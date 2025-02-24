# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/comp7_constants.py
from constants_utils import ConstInjector
from gui.limited_ui.lui_rules_storage import LUI_RULES
from gui.prb_control import settings
from messenger import m_constants
from gui.battle_control import battle_constants
ATTR_NAME = 'COMP7'
_LUI_RULE_ENTRY_POINT = 'Comp7EntryPoint'
_LUI_RULES = [_LUI_RULE_ENTRY_POINT]

class FUNCTIONAL_FLAG(settings.FUNCTIONAL_FLAG, ConstInjector):
    COMP7 = 536870912


class PREBATTLE_ACTION_NAME(settings.PREBATTLE_ACTION_NAME, ConstInjector):
    _const_type = str
    COMP7 = 'comp7'
    COMP7_SQUAD = 'comp7Squad'


class SELECTOR_BATTLE_TYPES(settings.SELECTOR_BATTLE_TYPES, ConstInjector):
    _const_type = str
    COMP7 = 'comp7'


class REQUEST_TYPE(settings.REQUEST_TYPE, ConstInjector):
    pass


class SCH_CLIENT_MSG_TYPE(m_constants.SCH_CLIENT_MSG_TYPE, ConstInjector):
    pass


class BATTLE_CTRL_ID(battle_constants.BATTLE_CTRL_ID, ConstInjector):
    COMP7_VOIP_CTRL = 102


def initComp7LimitedUIIds():
    LUI_RULES.inject(_LUI_RULES)
