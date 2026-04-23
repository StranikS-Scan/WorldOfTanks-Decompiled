# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/common/historical_battles_common/hb_constants_extension.py
import types
from functools import wraps
import constants
from constants_utils import ConstInjector
from constants_utils import AbstractBattleMode
from BattleFeedbackCommon import BATTLE_EVENT_TYPE as ORIG_BATTLE_EVENT_TYPE
from UnitBase import UNIT_MGR_FLAGS as ORIG_UNIT_MGR_FLAGS, ROSTER_TYPE as ORIG_ROSTER_TYPE, CLIENT_UNIT_CMD as ORIG_CLIENT_UNIT_CMD, UNIT_NOTIFY_CMD as ORIG_UNIT_NOTIFY_CMD
from historical_battles_common.hb_constants import HB_GAME_PARAMS_KEY
from historical_battles_common.battle_results import historical_battles

class ARENA_GUI_TYPE(constants.ARENA_GUI_TYPE, ConstInjector):
    HB_OFFENCE = 101
    HB_DEFENCE = 102
    HB_RANGE = (HB_OFFENCE, HB_DEFENCE)


class ARENA_BONUS_TYPE(constants.ARENA_BONUS_TYPE, ConstInjector):
    HB_OFFENCE = 101
    HB_DEFENCE = 102
    HB_RANGE = (HB_OFFENCE, HB_DEFENCE)


class QUEUE_TYPE(constants.QUEUE_TYPE, ConstInjector):
    HB_OFFENCE = 101
    HB_DEFENCE = 102
    HB_RANGE = (HB_OFFENCE, HB_DEFENCE)


class PREBATTLE_TYPE(constants.PREBATTLE_TYPE, ConstInjector):
    HISTORICAL_BATTLES = 101


class UNIT_MGR_FLAGS(ORIG_UNIT_MGR_FLAGS, ConstInjector):
    HB_OFFENCE = 2097152
    HB_DEFENCE = 4194304


HB_UNIT_MGR_FLAGS_GENERAL_MASK = UNIT_MGR_FLAGS.HB_OFFENCE | UNIT_MGR_FLAGS.HB_DEFENCE

class ROSTER_TYPE(ORIG_ROSTER_TYPE, ConstInjector):
    HB_OFFENCE = UNIT_MGR_FLAGS.SQUAD | UNIT_MGR_FLAGS.HB_OFFENCE
    HB_DEFENCE = UNIT_MGR_FLAGS.SQUAD | UNIT_MGR_FLAGS.HB_DEFENCE


HB_ROSTER_TYPE_GENERAL_MASK = UNIT_MGR_FLAGS.SQUAD | HB_UNIT_MGR_FLAGS_GENERAL_MASK
QUEUE_TYPE_TO_UNIT_DATA = {QUEUE_TYPE.HB_OFFENCE: (UNIT_MGR_FLAGS.HB_OFFENCE, ROSTER_TYPE.HB_OFFENCE),
 QUEUE_TYPE.HB_DEFENCE: (UNIT_MGR_FLAGS.HB_DEFENCE, ROSTER_TYPE.HB_DEFENCE)}

class INVITATION_TYPE(constants.INVITATION_TYPE, ConstInjector):
    HISTORICAL_BATTLES = PREBATTLE_TYPE.HISTORICAL_BATTLES


class CLIENT_UNIT_CMD(ORIG_CLIENT_UNIT_CMD, ConstInjector):
    SET_UNIT_FRONT = 1001
    START_UNIT_HISTORICAL_BATTLES = 1002
    SET_UNIT_DIVISION = 1003


class UNIT_NOTIFY_CMD(ORIG_UNIT_NOTIFY_CMD, ConstInjector):
    SET_NOTIFY_FRONT = 101
    SET_NOTIFY_DIVISION = 102


class BATTLE_EVENT_TYPE(ORIG_BATTLE_EVENT_TYPE, ConstInjector):
    HB_ACTION_APPLIED = 101
    HEAL_VEHICLE_APPLIED_ACTION = 102
    TOTAL_VEHICLES_HEAL_APPLIED_ACTION = 103
    HEAL_SELF_VEHICLE_APPLIED_ACTION = 104


INVALID_FRONT_ID = -1
INVALID_DIVISION_ID = 0
FRONT_QUEUE_TYPES = {'offence': QUEUE_TYPE.HB_OFFENCE,
 'defence': QUEUE_TYPE.HB_DEFENCE}
FRONT_BONUS_TYPES = {'offence': ARENA_BONUS_TYPE.HB_OFFENCE,
 'defence': ARENA_BONUS_TYPE.HB_DEFENCE}
QUEUE_TYPE_TO_BATTLE_MGR = {QUEUE_TYPE.HB_OFFENCE: 'HBOffenceBattleMgr',
 QUEUE_TYPE.HB_DEFENCE: 'HBDefenceBattleMgr'}

class HistoricalBattlesBattleMode(AbstractBattleMode):
    _PREBATTLE_TYPE = PREBATTLE_TYPE.HISTORICAL_BATTLES
    _QUEUE_TYPE = QUEUE_TYPE.HB_OFFENCE
    _ARENA_BONUS_TYPE = ARENA_BONUS_TYPE.HB_OFFENCE
    _ARENA_GUI_TYPE = ARENA_GUI_TYPE.HB_OFFENCE
    _GAME_PARAMS_KEY = HB_GAME_PARAMS_KEY
    _SM_TYPE_BATTLE_RESULT = 'hbBattleResults'
    _SM_TYPES = [_SM_TYPE_BATTLE_RESULT,
     'hbShopBundlePurchased',
     'hbCouponsBundlePurchased',
     'hbTankModuleBundlePurchased',
     'hbMainPrizeVehiclePurchased',
     'HBProgressionNotification',
     'hbDivisionUpgradeFinancialSuccess',
     'HBOrderInvoice']
    _BATTLE_RESULTS_CONFIG = historical_battles
    _ITERABLE_ARENA_BONUS_TYPE_HANDLERS = {'registerBattleResultSysMsgType', 'registerBattleResultsConfig'}

    def __getattribute__(self, name):
        attr = super(HistoricalBattlesBattleMode, self).__getattribute__(name)
        if name in HistoricalBattlesBattleMode._ITERABLE_ARENA_BONUS_TYPE_HANDLERS:
            wrapped = HistoricalBattlesBattleMode.__arenaBonusTypeVisitor(attr)
            return types.MethodType(wrapped, self)
        return attr

    @staticmethod
    def __arenaBonusTypeVisitor(method):

        @wraps(method)
        def visitor(self, *args, **kwargs):
            for arenaBonusType in ARENA_BONUS_TYPE.HB_RANGE:
                self._ARENA_BONUS_TYPE = arenaBonusType
                method(*args, **kwargs)

        return visitor
