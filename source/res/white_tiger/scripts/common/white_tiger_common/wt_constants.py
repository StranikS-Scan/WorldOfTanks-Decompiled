# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/common/white_tiger_common/wt_constants.py
import UnitBase
import constants
from enum import IntEnum
from constants_utils import ConstInjector, AbstractBattleMode
from battle_results import white_tiger
import BattleFeedbackCommon

class ARENA_GUI_TYPE(constants.ARENA_GUI_TYPE, ConstInjector):
    WHITE_TIGER = 301


class ARENA_BONUS_TYPE(constants.ARENA_BONUS_TYPE, ConstInjector):
    WHITE_TIGER = 52
    WHITE_TIGER_2 = 53
    WT_BATTLES_RANGE = (WHITE_TIGER, WHITE_TIGER_2)


class PREBATTLE_TYPE(constants.PREBATTLE_TYPE, ConstInjector):
    WHITE_TIGER = 301


class QUEUE_TYPE(constants.QUEUE_TYPE, ConstInjector):
    WHITE_TIGER = 301


class GameSeasonType(constants.GameSeasonType, ConstInjector):
    WHITE_TIGER = 9


class UNIT_MGR_FLAGS(UnitBase.UNIT_MGR_FLAGS, ConstInjector):
    WHITE_TIGER = 2097152


class ROSTER_TYPE(UnitBase.ROSTER_TYPE, ConstInjector):
    WHITE_TIGER = UNIT_MGR_FLAGS.SQUAD | UNIT_MGR_FLAGS.WHITE_TIGER


class INVITATION_TYPE(UnitBase.INVITATION_TYPE, ConstInjector):
    WHITE_TIGER = PREBATTLE_TYPE.WHITE_TIGER


class CLIENT_UNIT_CMD(UnitBase.CLIENT_UNIT_CMD, ConstInjector):
    WT_SQUAD_SELECT_VEHICLE = 2001


class BATTLE_EVENT_TYPE(BattleFeedbackCommon.BATTLE_EVENT_TYPE, ConstInjector):
    WT_VEHICLE_UNION_STRENGTH_MARK = 37
    WT_VEHICLE_STUN_AREA_DEBUFF = 38
    WT_VEHICLE_PLASMA_ON_BOSS = 39
    VEHICLE_DISCRETE_DAMAGE_RECEIVED = 40
    WT_VEHICLE_STUN_AREA_MOD_A_DEBUFF = 41
    WT_EXTRACTOR_SHOT_DEBUFF = 43


class REQUEST_COOLDOWN(constants.REQUEST_COOLDOWN, ConstInjector):
    ROLL_WT_LOOTBOX = 1.0
    REROLL_WT_LOOTBOX = 1.0
    CLAIM_WT_LOOTBOX = 1.0
    PENDING_WT_LOOTBOXES = 1.0


class WT_COMPONENT_NAMES(object):
    SHIELD_DEBUFF_ARENA_TIMER = 'wtShieldDebuffDuration'
    ACTIVATION_ARENA_TIMER = 'activationTimer'
    GENERATORS_COUNTER = 'wtCapturesTillEndgame'
    HYPERION_COUNTER = 'wtHyperionCharge'


class WT_COMPONENT_CONSTANTS(object):
    MISSILE_WIDGET_MAX_ALTITUDE = 150
    HYPERION_MAX_CHARGE = 100


class WT_BATTLE_STAGE(object):
    INVINCIBLE = 0
    DEBUFF = 1
    END_GAME = 2

    @staticmethod
    def getCurrent(arenaInfo):
        if WT_COMPONENT_NAMES.SHIELD_DEBUFF_ARENA_TIMER in arenaInfo.dynamicComponents:
            return WT_BATTLE_STAGE.DEBUFF
        return WT_BATTLE_STAGE.END_GAME if arenaInfo.wtArenaPublicInfo.generatorCounter == 0 else WT_BATTLE_STAGE.INVINCIBLE


class WT_TEAMS(object):
    BOSS_TEAM = 1
    HUNTERS_TEAM = 2


WHITE_TIGER_GAME_PARAMS_KEY = 'white_tiger_config'
WHITE_TIGER_BATTLE_PARAMS_KEY = 'white_tiger_battle_config'

class WhiteTigerBattleMode(AbstractBattleMode):
    _PREBATTLE_TYPE = PREBATTLE_TYPE.WHITE_TIGER
    _QUEUE_TYPE = QUEUE_TYPE.WHITE_TIGER
    _ARENA_BONUS_TYPE = ARENA_BONUS_TYPE.WHITE_TIGER
    _ARENA_GUI_TYPE = ARENA_GUI_TYPE.WHITE_TIGER
    _UNIT_MGR_FLAGS = UNIT_MGR_FLAGS.WHITE_TIGER
    _ROSTER_TYPE = ROSTER_TYPE.WHITE_TIGER
    _INVITATION_TYPE = INVITATION_TYPE.WHITE_TIGER
    _BATTLE_MGR_NAME = 'WhiteTigerBattlesMgr'
    _GAME_PARAMS_KEY = WHITE_TIGER_GAME_PARAMS_KEY
    _SEASON_TYPE_BY_NAME = 'white_tiger_battle'
    _SEASON_TYPE = GameSeasonType.WHITE_TIGER
    _SEASON_MANAGER_TYPE = (GameSeasonType.WHITE_TIGER, WHITE_TIGER_GAME_PARAMS_KEY)
    _BATTLE_RESULTS_CONFIG = white_tiger
    _SM_TYPE_BATTLE_RESULT = 'whiteTigerBattleResults'
    _SM_TYPES = [_SM_TYPE_BATTLE_RESULT, 'wtEventTicketTokenWithdrawn']

    @property
    def _ROSTER_CLASS(self):
        from white_tiger_common.wt_roster_config import WhiteTigerRoster
        return WhiteTigerRoster


class BarrierMode(IntEnum):
    DISABLED = 0
    DYNAMIC = 1
    STATIC = 2


class HealMode(IntEnum):
    MAX_HEALTH_PERCENT = 0
    FIXED = 1


class InvisibilityType(IntEnum):
    SENTINELS = 0
    BOSS = 1


class InvisibilityState(IntEnum):
    DISABLED = 0
    ACTIVATED = 1
    DEACTIVATED = 2


WT_REROLLABLE_BOX_CATEGORY = 'WTLootBoxRerollable'
PDATA_WT_KEY = 'white_tiger'
PDATA_WT_LOOTBOXES_KEY = 'wt_lootboxes'
WT_MAX_COUNT_TO_ROLL = 5
WT_MIN_COUNT_TO_ROLL = 1

class WTLootBoxError(object):
    UNKNOWN_BOX_ID = 'wt_lb_unknown_box_id'
    WRONG_CATEGORY = 'wt_lb_wrong_category'
    ROLL_FAILURE = 'wt_lb_roll_failure'
    ROLL_WHILE_PENDING = 'wt_lb_roll_while_pending'
    NOT_REROLL_BOX = 'wt_lb_not_reroll_box'
    EMPTY_REQUEST = 'wt_lb_empty_request'
    REROLL_FAILURE = 'wt_lb_reroll_failure'
    CLAIM_FAILURE = 'wt_lb_claim_failure'
    REROLLS_EXHAUSTED = 'wt_lb_rerolls_exhausted'
    EXTRAS_INVOICE_FAILURE = 'wt_lb_extras_invoice_failure'
