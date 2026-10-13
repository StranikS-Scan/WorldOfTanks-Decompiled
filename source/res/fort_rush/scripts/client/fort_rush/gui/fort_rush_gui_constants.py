# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/fort_rush_gui_constants.py
from __future__ import absolute_import
from constants_utils import ConstInjector
from gui.battle_control import battle_constants
from gui.prb_control import settings
from gui.Scaleform.daapi.settings import views
from messenger import m_constants
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _FET

class PREBATTLE_ACTION_NAME(settings.PREBATTLE_ACTION_NAME, ConstInjector):
    _const_type = str
    FORT_RUSH = 'fort_rush_battle'
    FORT_RUSH_SQUAD = 'fort_rush_squad'


class FUNCTIONAL_FLAG(settings.FUNCTIONAL_FLAG, ConstInjector):
    FORT_RUSH = 68719476736L


class SELECTOR_BATTLE_TYPES(settings.SELECTOR_BATTLE_TYPES, ConstInjector):
    _const_type = str
    FORT_RUSH = 'FortRushBattle'


class VIEW_ALIAS(views.VIEW_ALIAS, ConstInjector):
    _const_type = str
    FORT_RUSH_BATTLE_PAGE = 'FortRushBattlePage'


class FORT_RUSH_HANGAR_ALIASES(object):
    FORT_RUSH_ENTRY_POINT = 'FortRushEntryPoint'


class SCH_CLIENT_MSG_TYPE(m_constants.SCH_CLIENT_MSG_TYPE, ConstInjector):
    FORT_RUSH_MSG_TYPE = 201


class FEEDBACK_EVENT_ID(_FET, ConstInjector):
    FORT_RUSH_PERSONAL_POINTS_CHANGED = 104


class MINIMAP_CONTAINER_NAME(object):
    FORT_RUSH_DEPLOY = 'deploymentPoints'
    FORT_RUSH_ZONES = 'fortRush'


class BATTLE_CTRL_ID(battle_constants.BATTLE_CTRL_ID, ConstInjector):
    FORT_RUSH_GUI_CTRL = 107
