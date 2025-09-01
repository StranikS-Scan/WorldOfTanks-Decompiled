# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/common/white_tiger_common/wt_constants.py
import arena_bonus_type_caps
import constants
import UnitBase
from constants_utils import AbstractBattleMode, ConstInjector
from enum import Enum
from collections import namedtuple
from white_tiger_common.battle_results import white_tiger_results
UNKNOWN_EVENT_ID = 0

class WhiteTigerEfficiencyParameterCount(object):
    MIN = 3
    MAX = 5


class ARENA_GUI_TYPE(constants.ARENA_GUI_TYPE, ConstInjector):
    WHITE_TIGER = 110


class ARENA_BONUS_TYPE(constants.ARENA_BONUS_TYPE, ConstInjector):
    WHITE_TIGER = 110


class QUEUE_TYPE(constants.QUEUE_TYPE, ConstInjector):
    WHITE_TIGER = 110


class PREBATTLE_TYPE(constants.PREBATTLE_TYPE, ConstInjector):
    WHITE_TIGER = 110


class ATTACK_REASON(constants.ATTACK_REASON, ConstInjector):
    _const_type = str
    WHITE_TIGER_CIRCUIT_OVERLOAD = 'circuit_overload'


DAMAGE_INFO_CODES_PER_ATTACK_REASON = {ATTACK_REASON.WHITE_TIGER_CIRCUIT_OVERLOAD: 'DEATH_FROM_CIRCUIT_OVERLOAD'}
WT_FIRE_NOTIFICATION_CIRCUIT_OVERLOAD_BOSS = 'DEVICE_STARTED_FIRE_AT_CIRCUIT_OVERLOAD_BOSS'
WT_FIRE_NOTIFICATION_CIRCUIT_OVERLOAD_HARRIER = 'DEVICE_STARTED_FIRE_AT_CIRCUIT_OVERLOAD_HARRIER'

class ARENA_BONUS_TYPE_CAPS(arena_bonus_type_caps.ARENA_BONUS_TYPE_CAPS, ConstInjector):
    _const_type = str
    WHITE_TIGER = 'WHITE_TIGER'


class UNIT_MGR_FLAGS(UnitBase.UNIT_MGR_FLAGS, ConstInjector):
    WHITE_TIGER = 4194304


class ROSTER_TYPE(UnitBase.ROSTER_TYPE, ConstInjector):
    WHITE_TIGER = UNIT_MGR_FLAGS.SQUAD | UNIT_MGR_FLAGS.WHITE_TIGER


class INVITATION_TYPE(constants.INVITATION_TYPE, ConstInjector):
    WHITE_TIGER = PREBATTLE_TYPE.WHITE_TIGER


class CLIENT_UNIT_CMD(UnitBase.CLIENT_UNIT_CMD, ConstInjector):
    pass


WHITE_TIGER_GAME_PARAMS_KEY = 'white_tiger_config'
UNIT_WHITE_TIGER_EXTRA_DATA_KEY = 'whiteTigerData'

class WT_VEHICLE_TAGS(object):
    BOSS = 'wt_boss'
    HUNTER = 'wt_hunter'
    PRIORITY_BOSS = 'wt_special_boss'
    MINIBOSS = 'wt_mini_boss'
    BOT = 'wt_bot'
    EVENT_VEHS = frozenset((BOSS, HUNTER))


class WT_TEAMS(object):
    BOSS_TEAM = 1
    HUNTERS_TEAM = 2


class WT_BATTLE_STAGE(object):
    INVINCIBLE = 0
    DEBUFF = 1
    END_GAME = 2

    @staticmethod
    def getCurrent(arenaInfo):
        wtBattleStateComponent = arenaInfo.dynamicComponents.get('wtBattleStateComponent')
        if wtBattleStateComponent:
            if wtBattleStateComponent.isShieldDown:
                return WT_BATTLE_STAGE.DEBUFF
            if wtBattleStateComponent.generatorsLeft == 0:
                return WT_BATTLE_STAGE.END_GAME
        return WT_BATTLE_STAGE.INVINCIBLE


class WhiteTigerBattleMode(AbstractBattleMode):
    _PREBATTLE_TYPE = PREBATTLE_TYPE.WHITE_TIGER
    _QUEUE_TYPE = QUEUE_TYPE.WHITE_TIGER
    _ARENA_BONUS_TYPE = ARENA_BONUS_TYPE.WHITE_TIGER
    _ARENA_GUI_TYPE = ARENA_GUI_TYPE.WHITE_TIGER
    _INVITATION_TYPE = INVITATION_TYPE.WHITE_TIGER
    _UNIT_MGR_NAME = 'WhiteTigerUnitMgr'
    _UNIT_MGR_FLAGS = UNIT_MGR_FLAGS.WHITE_TIGER
    _BATTLE_MGR_NAME = 'WhiteTigerBattlesMgr'
    _ROSTER_TYPE = ROSTER_TYPE.WHITE_TIGER
    _BATTLE_RESULTS_CONFIG = white_tiger_results
    _REQUIRED_VEHICLE_TAGS = ('event_battles',)
    _FORBIDDEN_VEHICLE_TAGS = constants.BATTLE_MODE_VEHICLE_TAGS - {'event_battles'}
    _SM_TYPE_TOKEN_WITHDRAWN = 'wtTicketTokenWithdrawn'
    _SM_TYPE_BATTLE_RESULT = 'wtBattleResults'
    _SM_TYPES = [_SM_TYPE_BATTLE_RESULT, _SM_TYPE_TOKEN_WITHDRAWN]
    _CLIENT_BANNER_ENTRY_POINT_ALIAS = 'WhiteTigerEntryPoint'

    @property
    def _rosterClass(self):
        from white_tiger_common.wt_roster_config import WhiteTigerRoster
        return WhiteTigerRoster


class WhiteTigerKeys(Enum):
    LIVES_COUNT = 'livesCount'
    CAMP = 'camp'
    RESURRECT_TIME_LEFT = 'resurrectTimeLeft'
    RESURRECT_TIME_TOTAL = 'resurrectTimeTotal'
    SPEED = 'replaySpeed'

    @staticmethod
    def getKeys(static=True):
        return [] if static else [(WhiteTigerKeys.LIVES_COUNT.value, 0),
         (WhiteTigerKeys.CAMP.value, ''),
         (WhiteTigerKeys.RESURRECT_TIME_LEFT.value, 0.0),
         (WhiteTigerKeys.RESURRECT_TIME_TOTAL.value, 0.0),
         (WhiteTigerKeys.SPEED.value, 1.0)]

    @staticmethod
    def getSortingKeys(static=True):
        return [WhiteTigerKeys.LIVES_COUNT.value] if not static else []


WTHyperionTimerViewState = namedtuple('WTHyperionTimerViewState', ['visible', 'totalTime', 'finishTime'])

class WTGeneratorState(object):
    PROTECTED = 0
    VULNERABLE = 1
    BLOCKED = 2
    CAPTURED = 3


WT_GENERATOR = 'generator'
WT_GENERATOR_MAX_PROGRESS = 100.0
WT_MATCHMAKER_STATS_NAMES = ('wtCountBossWins', 'wtBossDequeuedByUserCount', 'wtHunterDequeuedByUserCount', 'wtHunterKickedFromQueueCount', 'wtBossKickedFromQueueCount', 'wtBossWaitTime', 'wtBossesWithQuickTicketCount', 'wtCompletedBattlesCount', 'wtHunterWaitTime')
WT_EVENT_TICKET_KEY = 'wtevent:ticket'
WT_LOOTBOX_TOKEN_KEYS = {'lootBox:25091901',
 'lootBox:25091902',
 'lootBox:25091903',
 'lootBox:25091904'}
WT_PROGRESSION_TOKEN_KEY = 'wtevent:stamp'
WT_PROGRESSION_ACHIEVEMENT = 'wt2025progression'
WT_EVENT_GOLDEN_TICKET_KEY = 'wtevent:event_vehicles_special'
WT_FIRST_TIME_EVENT_ENTER_TANK = 'usa:A120_M48A5_hound_TLXXL'
