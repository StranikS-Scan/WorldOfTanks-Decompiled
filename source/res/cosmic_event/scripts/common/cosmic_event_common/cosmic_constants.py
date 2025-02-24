# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/common/cosmic_event_common/cosmic_constants.py
import constants
import BattleFeedbackCommon
from constants_utils import ConstInjector, AbstractBattleMode
from battle_results import cosmic_event
from cosmic_event_common import Abilities
COSMIC_EVENT_ROCKET_BOOSTER = 'cosmic_event_rocket_booster'
COSMIC_EVENT_SHIELD = 'cosmic_event_shield'
COSMIC_EVENT_WAVE = 'cosmic_event_wave'
COSMIC_EVENT_STUN_SHOT = 'cosmic_event_stun_shot'
COSMIC_EVENT_BLACKHOLE = 'cosmic_event_black_hole'
COSMIC_EVENT_OVERCHARGE = 'cosmic_event_gravity_field'
COSMIC_EVENT_POWER_SHOT = 'cosmic_event_power_shot'
COSMIC_EVENT_RAPIDSHELLING = 'cosmic_event_hook_shot'
COSMIC_EVENT_RESPAWN_PROTECTION = 'respawn_protection'
COSMIC_EVENT_SHOOT_ABILITY_NAME_TO_ID = {COSMIC_EVENT_RAPIDSHELLING: Abilities.SNIPER_SHOT,
 COSMIC_EVENT_POWER_SHOT: Abilities.POWER_SHOT,
 COSMIC_EVENT_STUN_SHOT: Abilities.STUN_SHOT}

class ARENA_GUI_TYPE(constants.ARENA_GUI_TYPE, ConstInjector):
    COSMIC_EVENT = 300


class ARENA_BONUS_TYPE(constants.ARENA_BONUS_TYPE, ConstInjector):
    COSMIC_EVENT = 51


class PREBATTLE_TYPE(constants.PREBATTLE_TYPE, ConstInjector):
    COSMIC_EVENT = 300


class QUEUE_TYPE(constants.QUEUE_TYPE, ConstInjector):
    COSMIC_EVENT = 300


class GameSeasonType(constants.GameSeasonType, ConstInjector):
    COSMIC_EVENT = 8


class BATTLE_EVENT_TYPE(BattleFeedbackCommon.BATTLE_EVENT_TYPE, ConstInjector):
    COSMIC_KILL = 24
    COSMIC_ARTIFACT_SCAN = 25
    COSMIC_RAMMING = 26
    COSMIC_PICKUP_ABILITY = 27
    COSMIC_ABILITY_HIT = 28
    COSMIC_SHOT = 29
    COSMIC_ASSIST = 30
    COSMIC_FIRST_BLOOD = 31
    COSMIC_KILL_STREAK = 32
    COSMIC_PICKUP_MASTER = 33
    COSMIC_REVENGE = 34
    COSMIC_BOOST_ME = 35
    MAX_KILL_SERIES = 36


class LOOT_TYPE(constants.LOOT_TYPE, ConstInjector):
    COSMIC_BLACK_HOLE = 5
    COSMIC_GRAVITY_FIELD = 6
    COSMIC_SHOOTING = 7
    COSMIC_POWER_SHOT = 8


CosmicAbilityMap = {LOOT_TYPE.COSMIC_BLACK_HOLE: COSMIC_EVENT_BLACKHOLE,
 LOOT_TYPE.COSMIC_GRAVITY_FIELD: COSMIC_EVENT_OVERCHARGE,
 LOOT_TYPE.COSMIC_SHOOTING: COSMIC_EVENT_RAPIDSHELLING,
 LOOT_TYPE.COSMIC_POWER_SHOT: COSMIC_EVENT_POWER_SHOT}

class DailyQuestsDecorations(constants.DailyQuestsDecorations, ConstInjector):
    COSMIC_DESTROY_TANK = 'cosmic_kill_vehicles'
    COSMIC_PLAY_BATTLES = 'cosmic_play_battles'
    COSMIC_MARS_POINTS = 'cosmic_mars_points'


DailyQuestDecorationMap = {12: DailyQuestsDecorations.COSMIC_PLAY_BATTLES,
 13: DailyQuestsDecorations.COSMIC_DESTROY_TANK,
 14: DailyQuestsDecorations.COSMIC_MARS_POINTS}
COSMIC_EVENT_GAME_PARAMS_KEY = 'cosmic_event_battles_config'

def registerDailyQuestsDecorations(personality):
    DailyQuestsDecorations.inject(personality)
    for decorator_id in DailyQuestDecorationMap:
        msg = 'Quest decorator id collision: {}'.format(decorator_id)

    constants.DailyQuestDecorationMap = constants.DailyQuestDecorationMap.update(DailyQuestDecorationMap)


def registerLootTypes(personality):
    LOOT_TYPE.inject(personality)


class CosmicEventBattleMode(AbstractBattleMode):
    _PREBATTLE_TYPE = PREBATTLE_TYPE.COSMIC_EVENT
    _QUEUE_TYPE = QUEUE_TYPE.COSMIC_EVENT
    _ARENA_BONUS_TYPE = ARENA_BONUS_TYPE.COSMIC_EVENT
    _ARENA_GUI_TYPE = ARENA_GUI_TYPE.COSMIC_EVENT
    _BATTLE_MGR_NAME = 'CosmicEventBattlesMgr'
    _GAME_PARAMS_KEY = COSMIC_EVENT_GAME_PARAMS_KEY
    _SEASON_TYPE_BY_NAME = 'cosmic_event_battle'
    _SEASON_TYPE = GameSeasonType.COSMIC_EVENT
    _SEASON_MANAGER_TYPE = (GameSeasonType.COSMIC_EVENT, COSMIC_EVENT_GAME_PARAMS_KEY)
    _BATTLE_RESULTS_CONFIG = cosmic_event
    _SM_TYPE_BATTLE_RESULT = 'cosmicEventBattleResults'
    _SM_TYPES = [_SM_TYPE_BATTLE_RESULT]


COSMIC_KEY = 'cosmic_keys'
EVENT_STARTED_NOTIFICATION_VIEWED = 'event_started_notification_viewed'
LAST_PROGRESSION_VISITED_LEVEL = 'last_progression_visited_level'
SELECTED_VEHICLE_ID = 'selected_vehicle_id'
ACCOUNT_DEFAULT_SETTINGS = {COSMIC_KEY: {EVENT_STARTED_NOTIFICATION_VIEWED: False,
              LAST_PROGRESSION_VISITED_LEVEL: 0,
              SELECTED_VEHICLE_ID: 1}}
