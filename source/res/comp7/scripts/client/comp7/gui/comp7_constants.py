# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/comp7_constants.py
from comp7.gui.Scaleform.genConsts.COMP7_HANGAR_ALIASES import COMP7_HANGAR_ALIASES
from constants_utils import ConstInjector
from gui.prb_control import settings
from messenger import m_constants
COMP7_HANGAR_ALIAS = COMP7_HANGAR_ALIASES.COMP7_LOBBY_HANGAR
COMP7_ENTRY_POINT_ALIAS = 'Comp7EntryPoint'

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
