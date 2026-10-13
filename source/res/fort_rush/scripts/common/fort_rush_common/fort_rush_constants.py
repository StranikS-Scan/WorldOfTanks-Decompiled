# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/common/fort_rush_common/fort_rush_constants.py
from __future__ import absolute_import
import enum
import UnitBase
import arena_bonus_type_caps
import constants
from constants_utils import ConstInjector, AbstractBattleMode
from enum import Enum
from fort_rush_common.battle_results import fort_rush
from BattleFeedbackCommon import BATTLE_EVENT_TYPE as BET
FORT_RUSH_SCORE_COMPONENT = 'FortRushScoreComponent'
FORT_RUSH_DEVELOPMENT_HELPER = 'FortRushDevelopmentHelper'
FORT_RUSH_VEHICLE_RESPAWN_COMPONENT = 'FortRushVehicleRespawnComponent'
FORT_RUSH_VEHICLE_BATTLE_FEEDBACK_COMPONENT = 'FortRushVehicleBattleFeedbackComponent'
FORT_RUSH_HIGHLIGHTER = 'FortRushHighlighter'
VEHICLE_RESPAWN_COMPONENT = 'VehicleRespawnComponent'
SCORE_COMPONENT = 'ScoreComponent'
CAPTURE_POINT_INVADER_COMPONENT = 'CapturePointInvaderComponent'
FORT_RUSH_VEHICLE_STATS_COLLECTOR = 'FortRushVehicleStatsCollector'
FORT_RUSH_SOUND_PLAYER = 'FortRushSoundPlayerComponent'
FORT_RUSH_PDATA_KEY = 'fortRush'
FORT_RUSH_DAILY_GROUP_KEY = 'fortRushDailyGroup'
CAPTURE_POINT_NO_TEAM = 0

class CaptureStates(enum.IntEnum):
    NEUTRAL = 0
    CAPTURED = 1
    CAPTURING = 3
    DECREASING = 4
    CONTESTED = 5


class FortRushStats(enum.IntEnum):
    CAPTURES = 0
    NEUTRALIZES = 1
    FIRST_CAPTURES = 2
    CAPTOR_KILLS = 3
    ZONE_DAMAGE_DEALT = 4
    LT_NEUTRALIZES = 5
    RAMMING = 6
    HT_DAMAGE = 7
    ATSPG_DAMAGE = 8

    @staticmethod
    def getStringKey(value):
        return _STATS_KEY_MAPPING.get(value)


_STATS_KEY_MAPPING = {FortRushStats.CAPTURES: 'captures',
 FortRushStats.NEUTRALIZES: 'neutralizes',
 FortRushStats.FIRST_CAPTURES: 'firstCaptures',
 FortRushStats.CAPTOR_KILLS: 'captorKills',
 FortRushStats.ZONE_DAMAGE_DEALT: 'zoneDamageDealt',
 FortRushStats.LT_NEUTRALIZES: 'LTNeutralizes',
 FortRushStats.ATSPG_DAMAGE: 'ATSPGDamage',
 FortRushStats.HT_DAMAGE: 'HTDamage',
 FortRushStats.RAMMING: 'ramming'}

class CapturePointStateCtxKeys(Enum):
    PREVIOUS_STATE = 'previousState'
    CAPTURABLE_POINT_OWNER_TEAM = 'capturablePointOwnerTeam'
    POINT_NAME = 'pointName'


CAPTURE_POINT_STATE_CONTEXT_TEMPLATE = {CapturePointStateCtxKeys.PREVIOUS_STATE.value: CaptureStates.NEUTRAL.name,
 CapturePointStateCtxKeys.CAPTURABLE_POINT_OWNER_TEAM.value: CAPTURE_POINT_NO_TEAM,
 CapturePointStateCtxKeys.POINT_NAME.value: ''}

class EventStates(enum.Enum):
    START = 0
    PAUSE = 1
    RESUME = 2
    ENDED = 3


class ARENA_GUI_TYPE(constants.ARENA_GUI_TYPE, ConstInjector):
    FORT_RUSH = 103


class ARENA_BONUS_TYPE(constants.ARENA_BONUS_TYPE, ConstInjector):
    FORT_RUSH = 111


class QUEUE_TYPE(constants.QUEUE_TYPE, ConstInjector):
    FORT_RUSH = 112


class PREBATTLE_TYPE(constants.PREBATTLE_TYPE, ConstInjector):
    FORT_RUSH = 111


class UNIT_MGR_FLAGS(UnitBase.UNIT_MGR_FLAGS, ConstInjector):
    FORT_RUSH = 33554432


class ROSTER_TYPE(UnitBase.ROSTER_TYPE, ConstInjector):
    FORT_RUSH = UNIT_MGR_FLAGS.SQUAD | UNIT_MGR_FLAGS.FORT_RUSH


class INVITATION_TYPE(constants.INVITATION_TYPE, ConstInjector):
    FORT_RUSH = PREBATTLE_TYPE.FORT_RUSH


class CLIENT_UNIT_CMD(UnitBase.CLIENT_UNIT_CMD, ConstInjector):
    START_UNIT_FORT_RUSH_BATTLE = 1102


class GameSeasonType(constants.GameSeasonType, ConstInjector):
    FORT_RUSH = 11


class ARENA_BONUS_TYPE_CAPS(arena_bonus_type_caps.ARENA_BONUS_TYPE_CAPS, ConstInjector):
    _const_type = str
    FORT_RUSH = 'FORT_RUSH'


class FINISH_REASON(constants.FINISH_REASON, ConstInjector):
    FORT_RUSH_DRAW = 210
    FORT_RUSH_REASONS = (210,)


class BATTLE_EVENT_TYPE(BET, ConstInjector):
    FORT_RUSH_PERSONAL_SCORE_UPDATE = 103


def injectFinishReasonConst(personality):
    if not any((reason in FINISH_REASON.getExtraAttrs().values() for reason in FINISH_REASON.FORT_RUSH_REASONS)):
        FINISH_REASON.inject(personality)


EXTENSION_NAME = 'fort_rush'
EXT_GAME_PARAMS_KEY = 'fort_rush_battles_config'
EXT_MATCHMAKER_GAME_PARAMS_KEY = 'fort_rush_matchmaker_config'
EXT_VISUAL_SCRIPT_PARAMS_KEY = 'fort_rush_visual_script_config'
FORT_RUSH_VEHICLE_TAG = 'fort_rush'
FORT_RUSH_EXCLUDED_TAGS = constants.BATTLE_MODE_VEH_TAGS_EXCEPT_EVENT | {'testTank', 'maps_training'}
MAX_ELIGIBLE_VEHICLES = 256

class FortRushBattleMode(AbstractBattleMode):
    _PREBATTLE_TYPE = PREBATTLE_TYPE.FORT_RUSH
    _QUEUE_TYPE = QUEUE_TYPE.FORT_RUSH
    _ARENA_BONUS_TYPE = ARENA_BONUS_TYPE.FORT_RUSH
    _ARENA_GUI_TYPE = ARENA_GUI_TYPE.FORT_RUSH
    _INVITATION_TYPE = INVITATION_TYPE.FORT_RUSH
    _BATTLE_MGR_NAME = 'FortRushBattlesMgr'
    _UNIT_MGR_NAME = 'FortRushUnitMgr'
    _UNIT_MGR_FLAGS = UNIT_MGR_FLAGS.FORT_RUSH
    _ROSTER_TYPE = ROSTER_TYPE.FORT_RUSH
    _FAIRPLAY_VEHICLE_BATTLE_STATS_COMPONENT = 'FortRushFairplayVehicleBattleStatsComponent'
    _GAME_PARAMS_KEY = EXT_GAME_PARAMS_KEY
    _SEASON_TYPE_BY_NAME = 'fort_rush_battle'
    _SEASON_TYPE = GameSeasonType.FORT_RUSH
    _BATTLE_RESULTS_CONFIG = fort_rush
    _SM_TYPE_BATTLE_RESULT = 'fortRushBattleResults'
    _SM_TYPES = [_SM_TYPE_BATTLE_RESULT]
    _CLIENT_BANNER_ENTRY_POINT_ALIAS = 'FortRushEntryPoint'
    _NEW_VEHICLES_TAGS = (FORT_RUSH_VEHICLE_TAG,)
    _FORBIDDEN_VEHICLE_TAGS = FORT_RUSH_EXCLUDED_TAGS

    @property
    def _rosterClass(self):
        from fort_rush_common.fort_rush_roster_config import FortRushRoster
        return FortRushRoster
