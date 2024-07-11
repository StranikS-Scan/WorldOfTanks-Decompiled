# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/common/races_common/races_constants.py
import BattleFeedbackCommon
import constants
from battle_results import races
from constants_utils import ConstInjector, AbstractBattleMode
RACES_ROCKET_BOOSTER = 'races_rocket_booster'
RACES_SHIELD = 'races_shield'
RACES_POWER_IMPULSE = 'races_power_impulse'
RACES_RAPIDSHELLING = 'races_rapidshelling'
RACES_ABILITY_KEY_GARANT = 'garant'

class ARENA_GUI_TYPE(constants.ARENA_GUI_TYPE, ConstInjector):
    RACES = 400


class ARENA_BONUS_TYPE(constants.ARENA_BONUS_TYPE, ConstInjector):
    RACES = 52


class PREBATTLE_TYPE(constants.PREBATTLE_TYPE, ConstInjector):
    RACES = 400


class QUEUE_TYPE(constants.QUEUE_TYPE, ConstInjector):
    RACES = 400


class FINISH_REASON(constants.FINISH_REASON, ConstInjector):
    RACE_WIN = 201


class GameSeasonType(constants.GameSeasonType, ConstInjector):
    RACES = 9


class BATTLE_EVENT_TYPE(BattleFeedbackCommon.BATTLE_EVENT_TYPE, ConstInjector):
    RACES_SHOT = 30
    RACES_RAMMING = 31
    RACES_ELECTRICAL_SHOCK = 32
    RACES_BOOST = 33
    RACES_SHIELD = 34
    RACES_POWER_IMPULSE = 35


class LOOT_TYPE(constants.LOOT_TYPE, ConstInjector):
    RACES_RAPIDSHELLING = 9
    RACES_SHIELD = 10
    RACES_POWER_IMPULSE = 11
    RACES_ROCKET_BOOSTER = 12


RacesAbilityMap = {LOOT_TYPE.RACES_RAPIDSHELLING: RACES_RAPIDSHELLING,
 LOOT_TYPE.RACES_SHIELD: RACES_SHIELD,
 LOOT_TYPE.RACES_ROCKET_BOOSTER: RACES_ROCKET_BOOSTER,
 LOOT_TYPE.RACES_POWER_IMPULSE: RACES_POWER_IMPULSE}
RacesAbilityNameToCode = {RACES_RAPIDSHELLING: LOOT_TYPE.RACES_RAPIDSHELLING,
 RACES_SHIELD: LOOT_TYPE.RACES_SHIELD,
 RACES_ROCKET_BOOSTER: LOOT_TYPE.RACES_ROCKET_BOOSTER,
 RACES_POWER_IMPULSE: LOOT_TYPE.RACES_POWER_IMPULSE}

class RacesBattleMode(AbstractBattleMode):
    _PREBATTLE_TYPE = PREBATTLE_TYPE.RACES
    _QUEUE_TYPE = QUEUE_TYPE.RACES
    _ARENA_BONUS_TYPE = ARENA_BONUS_TYPE.RACES
    _ARENA_GUI_TYPE = ARENA_GUI_TYPE.RACES
    _BATTLE_MGR_NAME = 'RacesBattlesMgr'
    _GAME_PARAMS_KEY = constants.Configs.RACES_CONFIG.value
    _SEASON_TYPE_BY_NAME = 'races_battle'
    _SEASON_TYPE = GameSeasonType.RACES
    _SEASON_MANAGER_TYPE = (GameSeasonType.RACES, constants.Configs.RACES_CONFIG.value)
    _BATTLE_RESULTS_CONFIG = races
    _SM_TYPE_BATTLE_RESULT = 'RacesBattleResults'
    _SM_TYPES = [_SM_TYPE_BATTLE_RESULT]


FINISH_ZONE_TRIGGER_EVENT_ID = 'vehicleEnterFinishZone'
PATH_DETECTOR_RADIUS = 100
PATH_DETECTOR_HEIGHT = 20
PATH_DETECTOR_DEEP = 10
