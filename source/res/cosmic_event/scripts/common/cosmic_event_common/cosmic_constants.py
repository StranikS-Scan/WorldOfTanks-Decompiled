# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/common/cosmic_event_common/cosmic_constants.py
import constants
import BattleFeedbackCommon
from constants_utils import ConstInjector, AbstractBattleMode
from enum import IntEnum
from battle_results import cosmic_event
from cosmic_event_common import Abilities
COSMIC_EVENT_RESPAWN_PROTECTION = 'respawn_protection'
COSMIC_EVENT_ROCKET_BOOSTER = 'cosmic_event_rocket_booster'
COSMIC_EVENT_SHIELD = 'cosmic_event_shield'
COSMIC_EVENT_WAVE = 'cosmic_event_wave'
COSMIC_EVENT_STUN_SHOT = 'cosmic_event_stun_shot'
COSMIC_EVENT_MINE = 'cosmic_event_mine'
COSMIC_EVENT_TELEPORT = 'cosmic_event_teleport'
COSMIC_EVENT_BLACKHOLE = 'cosmic_event_black_hole'
COSMIC_EVENT_OVERCHARGE = 'cosmic_event_gravity_field'
COSMIC_EVENT_POWER_SHOT = 'cosmic_event_power_shot'
COSMIC_EVENT_RAPIDSHELLING = 'cosmic_event_hook_shot'
COSMIC_EVENT_CORAL = 'cosmic_event_coral'
SPEED_BUFF = 'speed_buff'
MINE_ENTITY_NAME = 'RepulsionMine'
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
    MAX_KILL_SERIES = 33
    LOOT_RESEARCHING = 34
    LOOT_RESEARCHING_DONE = 35
    LOOT_RESEARCHABLE_PICK_UP = 36


class LOOT_ITEM_ID(IntEnum):
    COSMIC_BLACK_HOLE = 1
    COSMIC_GRAVITY_FIELD = 2
    COSMIC_SHOOTING = 3
    COSMIC_POWER_SHOT = 4
    COSMIC_CORAL = 5
    COSMIC_TELEPORT = 6
    SPEED_BUFF = 7


class LOOT_STATE(IntEnum):
    NOT_SPAWNED = 0
    PREPARING = 1
    SPAWNED = 2
    PICKED_UP = 3


class LOOT_TYPE(object):
    UNDEFINED = 'undefined'
    ABILITY = 'ability'
    RESEARCHABLE = 'researchable'
    BUFF = 'buff'


LOOT_TO_EQUIPMENT = {LOOT_ITEM_ID.COSMIC_BLACK_HOLE: COSMIC_EVENT_BLACKHOLE,
 LOOT_ITEM_ID.COSMIC_GRAVITY_FIELD: COSMIC_EVENT_OVERCHARGE,
 LOOT_ITEM_ID.COSMIC_SHOOTING: COSMIC_EVENT_RAPIDSHELLING,
 LOOT_ITEM_ID.COSMIC_POWER_SHOT: COSMIC_EVENT_POWER_SHOT,
 LOOT_ITEM_ID.COSMIC_TELEPORT: COSMIC_EVENT_TELEPORT}
LOOT_DESCRIPTION_TO_ID = {COSMIC_EVENT_BLACKHOLE: LOOT_ITEM_ID.COSMIC_BLACK_HOLE,
 COSMIC_EVENT_RAPIDSHELLING: LOOT_ITEM_ID.COSMIC_SHOOTING,
 COSMIC_EVENT_OVERCHARGE: LOOT_ITEM_ID.COSMIC_GRAVITY_FIELD,
 COSMIC_EVENT_POWER_SHOT: LOOT_ITEM_ID.COSMIC_POWER_SHOT,
 COSMIC_EVENT_CORAL: LOOT_ITEM_ID.COSMIC_CORAL,
 COSMIC_EVENT_TELEPORT: LOOT_ITEM_ID.COSMIC_TELEPORT,
 SPEED_BUFF: LOOT_ITEM_ID.SPEED_BUFF}

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

    constants.DailyQuestDecorationMap.update(DailyQuestDecorationMap)


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
COSMIC_MODE_SELECTOR_BATTLE_PASS_SHOWN = 'cosmic_mode_selector_battle_pass_shown'
SELECTED_VEHICLE_ID = 'selected_vehicle_id'
COSMIC_LOBBY_FIRST_ENTER_SOUND_PLAYED = 'cosmic_lobby_first_enter_sound'
COSMIC_INTRO_VIDEO_VIEWED = 'cosmic_intro_video_viewed'
ACCOUNT_DEFAULT_SETTINGS = {COSMIC_KEY: {EVENT_STARTED_NOTIFICATION_VIEWED: False,
              LAST_PROGRESSION_VISITED_LEVEL: 0,
              COSMIC_MODE_SELECTOR_BATTLE_PASS_SHOWN: False,
              SELECTED_VEHICLE_ID: 1,
              COSMIC_LOBBY_FIRST_ENTER_SOUND_PLAYED: False,
              COSMIC_INTRO_VIDEO_VIEWED: False}}
