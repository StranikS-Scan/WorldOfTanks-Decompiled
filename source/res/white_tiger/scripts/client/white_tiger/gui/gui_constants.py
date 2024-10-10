# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/gui_constants.py
from enum import Enum
from constants_utils import ConstInjector
from gui.prb_control import settings
from personal_missions_constants import CONDITION_ICON
from gui.server_events import cond_formatters
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS as _VEHICLE_TAGS
from gui.shared.gui_items.Vehicle import Vehicle
from white_tiger_common.wt_constants import WT_TAGS
from messenger import m_constants
import logging
_logger = logging.getLogger(__name__)

class VEHICLE_TAGS(_VEHICLE_TAGS, ConstInjector):
    WT_BOSS = WT_TAGS.WT_BOSS
    WT_HUNTER = WT_TAGS.WT_HUNTER
    WT_BOT = WT_TAGS.WT_BOT
    WT_SPECIAL_BOSS = WT_TAGS.WT_SPECIAL_BOSS
    WT_VEHICLES = frozenset((WT_BOSS, WT_HUNTER))


class VEHICLE_STATE(Vehicle.VEHICLE_STATE, ConstInjector):
    WT_TICKETS_SHORTAGE = 'ticketsShortage'


class WTPrebattleTypes(Enum):
    WHITE_TIGER = 'white_tiger'


class SCH_CLIENT_MSG_TYPE(m_constants.SCH_CLIENT_MSG_TYPE, ConstInjector):
    WT_EVENT_STATE = 600


BATTLE_RESULTS_KEYS = {'wtBossVulnerableDamage': CONDITION_ICON.DAMAGE,
 'maxWtPlasmaBonus': CONDITION_ICON.IMPROVE,
 'wtGeneratorsCaptured': CONDITION_ICON.BASE_CAPTURE,
 'wtTotalGeneratorsCaptured': CONDITION_ICON.BASE_CAPTURE,
 'wtDeathCount': CONDITION_ICON.SURVIVE}
ATTR_NAME = 'WHITE_TIGER'

class PREBATTLE_ACTION_NAME(settings.PREBATTLE_ACTION_NAME, ConstInjector):
    _const_type = str
    WHITE_TIGER = 'white_tiger'
    WHITE_TIGER_SQUAD = 'whiteTigerSquad'


class FUNCTIONAL_FLAG(settings.FUNCTIONAL_FLAG, ConstInjector):
    WHITE_TIGER = 4611686018427387904L


class SELECTOR_BATTLE_TYPES(settings.SELECTOR_BATTLE_TYPES, ConstInjector):
    _const_type = str
    WHITE_TIGER = 'WhiteTiger'


def injectClientConstants(personality):
    cond_formatters.BATTLE_RESULTS_KEYS.update(BATTLE_RESULTS_KEYS)
    VEHICLE_STATE.inject(personality)
    _custom = list(VEHICLE_STATE.CUSTOM)
    _custom.append(Vehicle.VEHICLE_STATE.WT_TICKETS_SHORTAGE)
    Vehicle.VEHICLE_STATE.CUSTOM = tuple(_custom)
    _unsuitable = list(VEHICLE_STATE.UNSUITABLE)
    _unsuitable.append(Vehicle.VEHICLE_STATE.WT_TICKETS_SHORTAGE)
    Vehicle.VEHICLE_STATE.UNSUITABLE = tuple(_unsuitable)
    _critStates = list(Vehicle.VEHICLE_STATE.CRIT_STATES)
    _critStates.append(Vehicle.VEHICLE_STATE.WT_TICKETS_SHORTAGE)
    Vehicle.VEHICLE_STATE.CRIT_STATES = tuple(_critStates)
    VEHICLE_TAGS.inject(personality)
