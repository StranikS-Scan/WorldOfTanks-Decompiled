# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/grinch_gui_constants.py
import CommandMapping
from constants_utils import ConstInjector
from gui.prb_control import settings
from gui.Scaleform.daapi.settings import views
from gui.server_events import cond_formatters
from messenger import m_constants
from personal_missions_constants import CONDITION_ICON
ABILITY_PANEL_COMMANDS_START = CommandMapping.CMD_AMMO_CHOICE_1

class FUNCTIONAL_FLAG(settings.FUNCTIONAL_FLAG, ConstInjector):
    GRINCH = 8589934592L


class PREBATTLE_ACTION_NAME(settings.PREBATTLE_ACTION_NAME, ConstInjector):
    _const_type = str
    GRINCH = 'grinch'
    GRINCH_SQUAD = 'grinchSquad'


class SELECTOR_BATTLE_TYPES(settings.SELECTOR_BATTLE_TYPES, ConstInjector):
    _const_type = str
    GRINCH = 'grinch'


class VIEW_ALIAS(views.VIEW_ALIAS, ConstInjector):
    _const_type = str
    GRINCH_BATTLE_PAGE = 'grinchBattlePage'
    GRINCH_LOADING = 'grinchLoading'
    GRINCH_SETTINGS_WINDOW = 'grinchSettingsWindow'


class SCH_CLIENT_MSG_TYPE(m_constants.SCH_CLIENT_MSG_TYPE, ConstInjector):
    GRINCH_EVENT_STATE = 421
    GRINCH_EVENT_PROGRESSION = 422


BATTLE_RESULTS_KEYS = {'grinch/rageDamage': CONDITION_ICON.EXPERIENCE,
 'grinch/frozenKill': CONDITION_ICON.EXPERIENCE,
 'grinch/closeRangeDamage': CONDITION_ICON.EXPERIENCE,
 'grinch/heal': CONDITION_ICON.EXPERIENCE,
 'grinch/turretDamage': CONDITION_ICON.EXPERIENCE,
 'grinch/carrierKilled': CONDITION_ICON.EXPERIENCE,
 'grinch/presentsStealthTheft': CONDITION_ICON.EXPERIENCE,
 'grinch/presentsDelivery': CONDITION_ICON.EXPERIENCE,
 'grinch/flaredDamage': CONDITION_ICON.EXPERIENCE}
cond_formatters.BATTLE_RESULTS_KEYS.update(BATTLE_RESULTS_KEYS)
