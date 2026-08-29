# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/gui_constants.py
from enum import Enum
from constants_utils import ConstInjector
from gui.prb_control import settings
from personal_missions_constants import CONDITION_ICON
from gui.server_events import cond_formatters
from gui.shared.gui_items.Vehicle import Vehicle
from gui.battle_control import battle_constants
from gui.battle_control.controllers import feedback_events
from white_tiger_common.wt_constants import BATTLE_EVENT_TYPE
from messenger import m_constants
import logging
_logger = logging.getLogger(__name__)

class FEEDBACK_EVENT_ID(battle_constants.FEEDBACK_EVENT_ID, ConstInjector):
    WT_VEHICLE_UNION_STRENGTH_MARK = 100
    WT_VEHICLE_STUN_AREA_DEBUFF = 101
    WT_VEHICLE_PLASMA_ON_BOSS = 102
    WT_VEHICLE_SILENCE = 103
    WT_VEHICLE_STUN_AREA_MOD_A_DEBUFF = 104
    WT_EXTRACTOR_SHOT_DEBUFF = 105
    WT_INVISIBILITY_MARK = 106


class VEHICLE_STATE(Vehicle.VEHICLE_STATE, ConstInjector):
    WT_TICKETS_SHORTAGE = 'ticketsShortage'


class WTPrebattleTypes(Enum):
    WHITE_TIGER = 'white_tiger'


class SCH_CLIENT_MSG_TYPE(m_constants.SCH_CLIENT_MSG_TYPE, ConstInjector):
    WT_EVENT_STATE = 600
    WT_ARENA_BAN_NOTIFICATIONS = 601
    WT_ARENA_ATTENTION_NOTIFICATIONS = 602
    WT_SWITCH_ON_LOOTBOXES_NOTIFICATIONS = 603
    WT_PROGRESSION = 604


BATTLE_RESULTS_KEYS = {'wtBossVulnerableDamage': CONDITION_ICON.DAMAGE,
 'maxWtPlasmaBonus': CONDITION_ICON.IMPROVE,
 'wtGeneratorsCaptured': CONDITION_ICON.BASE_CAPTURE,
 'wtTotalGeneratorsCaptured': CONDITION_ICON.BASE_CAPTURE,
 'wtDeathCount': CONDITION_ICON.SURVIVE}
_BATTLE_EVENT_TO_PLAYER_FEEDBACK_EVENT = {BATTLE_EVENT_TYPE.WT_VEHICLE_UNION_STRENGTH_MARK: FEEDBACK_EVENT_ID.WT_VEHICLE_UNION_STRENGTH_MARK,
 BATTLE_EVENT_TYPE.WT_VEHICLE_STUN_AREA_DEBUFF: FEEDBACK_EVENT_ID.WT_VEHICLE_STUN_AREA_DEBUFF,
 BATTLE_EVENT_TYPE.WT_VEHICLE_PLASMA_ON_BOSS: FEEDBACK_EVENT_ID.WT_VEHICLE_PLASMA_ON_BOSS,
 BATTLE_EVENT_TYPE.WT_EXTRACTOR_SHOT_DEBUFF: FEEDBACK_EVENT_ID.WT_EXTRACTOR_SHOT_DEBUFF}
_PLAYER_FEEDBACK_EXTRA_DATA_CONVERTERS = {FEEDBACK_EVENT_ID.WT_VEHICLE_UNION_STRENGTH_MARK: feedback_events._unpackInteger,
 FEEDBACK_EVENT_ID.WT_VEHICLE_STUN_AREA_DEBUFF: feedback_events._unpackInteger,
 FEEDBACK_EVENT_ID.WT_VEHICLE_PLASMA_ON_BOSS: feedback_events._unpackInteger,
 FEEDBACK_EVENT_ID.WT_EXTRACTOR_SHOT_DEBUFF: feedback_events._unpackInteger}
ATTR_NAME = 'WHITE_TIGER'

class PREBATTLE_ACTION_NAME(settings.PREBATTLE_ACTION_NAME, ConstInjector):
    _const_type = str
    WHITE_TIGER = 'white_tiger'
    WHITE_TIGER_SQUAD = 'whiteTigerSquad'


class FUNCTIONAL_FLAG(settings.FUNCTIONAL_FLAG, ConstInjector):
    WHITE_TIGER = 4611686018427387904L


class SELECTOR_BATTLE_TYPES(settings.SELECTOR_BATTLE_TYPES, ConstInjector):
    _const_type = str
    WHITE_TIGER = 'white_tiger'


def injectClientConstants(personality):
    feedback_events._BATTLE_EVENT_TO_PLAYER_FEEDBACK_EVENT.update(_BATTLE_EVENT_TO_PLAYER_FEEDBACK_EVENT)
    feedback_events._PLAYER_FEEDBACK_EXTRA_DATA_CONVERTERS.update(_PLAYER_FEEDBACK_EXTRA_DATA_CONVERTERS)
    cond_formatters.BATTLE_RESULTS_KEYS.update(BATTLE_RESULTS_KEYS)
    VEHICLE_STATE.inject(personality)
    _custom = list(VEHICLE_STATE.CUSTOM)
    _custom.append(Vehicle.VEHICLE_STATE.WT_TICKETS_SHORTAGE)
    Vehicle.VEHICLE_STATE.CUSTOM = tuple(_custom)
    _unsuitable = list(VEHICLE_STATE.UNSUITABLE)
    _unsuitable.append(Vehicle.VEHICLE_STATE.WT_TICKETS_SHORTAGE)
    Vehicle.VEHICLE_STATE.UNSUITABLE = tuple(_unsuitable)
