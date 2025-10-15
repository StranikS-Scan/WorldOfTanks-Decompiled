# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/portal_gui_constants.py
from enum import Enum
from constants_utils import ConstInjector
from gui.prb_control import settings
from gui.Scaleform.daapi.settings import views
from messenger import m_constants
from portal.gui.Scaleform.genConsts.PORTAL_BATTLE_VIEW_ALIASES import PORTAL_BATTLE_VIEW_ALIASES
CAMP_ORDER = ['Tsarev',
 'Yaginskaya',
 'Vasilieva',
 'Koshcheeva']
CAMP_ORDER_INDEX = {v:i for i, v in enumerate(CAMP_ORDER)}

class PREBATTLE_ACTION_NAME(settings.PREBATTLE_ACTION_NAME, ConstInjector):
    _const_type = str
    PORTAL_BATTLE = 'portal_battle'
    PORTAL_BATTLE_SQUAD = 'portal_squad'


class FUNCTIONAL_FLAG(settings.FUNCTIONAL_FLAG, ConstInjector):
    PORTAL = 1073741824


class SELECTOR_BATTLE_TYPES(settings.SELECTOR_BATTLE_TYPES, ConstInjector):
    _const_type = str
    PORTAL = 'PortalBattle'


class VIEW_ALIAS(views.VIEW_ALIAS, ConstInjector):
    _const_type = str
    PORTAL_BATTLE_PAGE = PORTAL_BATTLE_VIEW_ALIASES.PORTAL_BATTLE_PAGE


class SCH_CLIENT_MSG_TYPE(m_constants.SCH_CLIENT_MSG_TYPE, ConstInjector):
    PORTAL_MSG_TYPE = 700


class REQUEST_TYPE(settings.REQUEST_TYPE, ConstInjector):
    PORTAL_SET_BATTLE_LEVEL = 48


class PortalPrebattleTypes(Enum):
    PORTAL = 'portal'
