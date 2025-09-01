# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/comp7_light_constants.py
from comp7_light.gui.Scaleform.genConsts.COMP7_LIGHT_HANGAR_ALIASES import COMP7_LIGHT_HANGAR_ALIASES
from constants_utils import ConstInjector
from gui.prb_control import settings
from messenger import m_constants
COMP7_HANGAR_ALIAS = COMP7_LIGHT_HANGAR_ALIASES.COMP7_LIGHT_LOBBY_HANGAR
COMP7_LIGHT_ENTRY_POINT_ALIAS = 'Comp7LightEntryPoint'

class FUNCTIONAL_FLAG(settings.FUNCTIONAL_FLAG, ConstInjector):
    COMP7_LIGHT = 34359738368L


class PREBATTLE_ACTION_NAME(settings.PREBATTLE_ACTION_NAME, ConstInjector):
    _const_type = str
    COMP7_LIGHT = 'comp7Light'
    COMP7_LIGHT_SQUAD = 'comp7LightSquad'


class SELECTOR_BATTLE_TYPES(settings.SELECTOR_BATTLE_TYPES, ConstInjector):
    _const_type = str
    COMP7_LIGHT = 'comp7Light'


class SCH_CLIENT_MSG_TYPE(m_constants.SCH_CLIENT_MSG_TYPE, ConstInjector):
    COMP7_LIGHT_PROGRESSION_NOTIFICATIONS = 301
