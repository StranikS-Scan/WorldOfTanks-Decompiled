# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/common/last_stand_common/last_stand_constants.py
import enum
import constants
import UnitBase
import arena_bonus_type_caps
from constants_utils import ConstInjector, AbstractBattleMode
from last_stand_common.battle_results import ls_results
from BattleFeedbackCommon import BATTLE_EVENT_TYPE as BET

class ARENA_GUI_TYPE(constants.ARENA_GUI_TYPE, ConstInjector):
    LAST_STAND = 102


class ARENA_BONUS_TYPE(constants.ARENA_BONUS_TYPE, ConstInjector):
    LAST_STAND = 107
    LAST_STAND_MEDIUM = 108
    LAST_STAND_HARD = 109


LAST_STAND_ARENA_BONUS_TYPES = (ARENA_BONUS_TYPE.LAST_STAND, ARENA_BONUS_TYPE.LAST_STAND_MEDIUM, ARENA_BONUS_TYPE.LAST_STAND_HARD)

class QUEUE_TYPE(constants.QUEUE_TYPE, ConstInjector):
    LAST_STAND = 107
    LAST_STAND_MEDIUM = 108
    LAST_STAND_HARD = 109


class PREBATTLE_TYPE(constants.PREBATTLE_TYPE, ConstInjector):
    LAST_STAND = 102


class UNIT_MGR_FLAGS(UnitBase.UNIT_MGR_FLAGS, ConstInjector):
    LAST_STAND = 8388608


class ROSTER_TYPE(UnitBase.ROSTER_TYPE, ConstInjector):
    LAST_STAND = UNIT_MGR_FLAGS.SQUAD | UNIT_MGR_FLAGS.LAST_STAND


class INVITATION_TYPE(constants.INVITATION_TYPE, ConstInjector):
    LAST_STAND = PREBATTLE_TYPE.LAST_STAND


class CLIENT_UNIT_CMD(UnitBase.CLIENT_UNIT_CMD, ConstInjector):
    SET_LS_UNIT_DIFFICULTY_LEVEL = 2002


UNIT_LS_EXTRA_DATA_KEY = 'LS_Data'
UNIT_DIFFICULTY_LEVELS_KEY = 'LS_difficultyLevels'
REQUIRED_VEHICLE_TAGS = {}
FORBIDDEN_VEHICLE_TAGS = (constants.BATTLE_MODE_VEHICLE_TAGS | {'testTank'}) - {'event_battles'}

class ATTACK_REASON(constants.ATTACK_REASON, ConstInjector):
    _const_type = str
    LS_BOMBER_EXPLOSION = 'ls_bomber_explosion'
    LS_ABILITY_VAMPIRE = 'ls_ability_vampire'
    LS_ABILITY_AOE_DAMAGE = 'ls_ability_aoe_damage'
    LS_ABILITY_IGNITE = 'ls_ability_ignite'
    LS_PHASE_TIMER = 'ls_phase_timer'
    LS_LEAVER = 'ls_leaver'
    LS_PASSIVE_IGNITE = 'ls_passive_ignite'
    LS_PASSIVE_VAMPIRE = 'ls_passive_vampire'
    LS_DEATH_PIT = 'ls_death_pit'
    LS_SHOT_AOE_DAMAGE = 'ls_shot_aoe_damage'
    LS_SHOT_AOE_DRAIN_ENEMY_HP = 'ls_shot_aoe_drain_enemy_hp'
    LS_SHOT_AOE_STUN = 'ls_shot_aoe_stun'
    LS_EXTRA_DAMAGE_SITUATIONAL = 'ls_extra_damage_situational'


DAMAGE_INFO_CODES_PER_ATTACK_REASON = {ATTACK_REASON.LS_BOMBER_EXPLOSION: 'DEATH_FROM_LS_BOMBER_EXPLOSION',
 ATTACK_REASON.LS_ABILITY_VAMPIRE: 'DEATH_FROM_LS_ABILITY_VAMPIRE',
 ATTACK_REASON.LS_ABILITY_AOE_DAMAGE: 'DEATH_FROM_LS_ABILITY_AOE_DAMAGE',
 ATTACK_REASON.LS_ABILITY_IGNITE: 'DEATH_FROM_LS_ABILITY_IGNITE',
 ATTACK_REASON.LS_PHASE_TIMER: 'DEATH_FROM_LS_PHASE_TIMER',
 ATTACK_REASON.LS_LEAVER: 'DEATH_FROM_LS_PHASE_TIMER',
 ATTACK_REASON.LS_PASSIVE_IGNITE: 'DEATH_FROM_FIRE',
 ATTACK_REASON.LS_PASSIVE_VAMPIRE: 'DEATH_FROM_LS_PASSIVE_VAMPIRE',
 ATTACK_REASON.LS_DEATH_PIT: 'DEATH_FROM_LS_DEATH_PIT',
 ATTACK_REASON.LS_SHOT_AOE_DAMAGE: 'DEATH_FROM_LS_SHOT_AOE_DAMAGE',
 ATTACK_REASON.LS_SHOT_AOE_STUN: 'DEATH_FROM_LS_SHOT_AOE_STUN',
 ATTACK_REASON.LS_SHOT_AOE_DRAIN_ENEMY_HP: 'DEATH_FROM_LS_SHOT_AOE_DRAIN_ENEMY_HP',
 ATTACK_REASON.LS_EXTRA_DAMAGE_SITUATIONAL: 'DEATH_FROM_LS_EXTRA_DAMAGE_SITUATIONAL'}

class ARENA_BONUS_TYPE_CAPS(arena_bonus_type_caps.ARENA_BONUS_TYPE_CAPS, ConstInjector):
    _const_type = str
    LAST_STAND = 'LAST_STAND'


LAST_STAND_GAME_PARAMS_KEY = 'last_stand_config'
ENEMY_ROLE_TAG_PREFIX = 'lsrole_'
LS_ROLE_PREFIX = 'ls_'
LS_BOMBER_ACTIVATE_REASON = (ATTACK_REASON.SHOT,
 ATTACK_REASON.LS_ABILITY_AOE_DAMAGE,
 ATTACK_REASON.LS_ABILITY_VAMPIRE,
 ATTACK_REASON.LS_SHOT_AOE_DAMAGE,
 ATTACK_REASON.LS_SHOT_AOE_STUN,
 ATTACK_REASON.LS_SHOT_AOE_DRAIN_ENEMY_HP)
PLAYERS_TEAM = 1
INVALID_BATTLE_PLACE = -1

class LastStandBattleMode(AbstractBattleMode):
    _PREBATTLE_TYPE = PREBATTLE_TYPE.LAST_STAND
    _QUEUE_TYPE = QUEUE_TYPE.LAST_STAND
    _ARENA_BONUS_TYPE = ARENA_BONUS_TYPE.LAST_STAND
    _ARENA_GUI_TYPE = ARENA_GUI_TYPE.LAST_STAND
    _INVITATION_TYPE = INVITATION_TYPE.LAST_STAND
    _BATTLE_MGR_NAME = 'LSBattlesMgr'
    _UNIT_MGR_NAME = 'LSUnitMgr'
    _UNIT_MGR_FLAGS = UNIT_MGR_FLAGS.LAST_STAND
    _ROSTER_TYPE = ROSTER_TYPE.LAST_STAND
    _GAME_PARAMS_KEY = LAST_STAND_GAME_PARAMS_KEY
    _BATTLE_RESULTS_CONFIG = ls_results
    _REQUIRED_VEHICLE_TAGS = REQUIRED_VEHICLE_TAGS
    _FORBIDDEN_VEHICLE_TAGS = FORBIDDEN_VEHICLE_TAGS
    _SM_TYPE_ARTEFACT_REWARD_CONGRATS = 'lsArtefactRewardCongrats'
    _SM_TYPE_DIFFICULTY_REWARD_CONGRATS = 'lsDifficultyRewardCongrats'
    _SM_TYPE_DIFFICULTY_OPEN_MESSAGE = 'lsDifficultyOpenMessage'
    _SM_TYPE_ARTEFACT_KEYS_MESSAGE = 'lsArtefactKeysMessage'
    _SM_TYPE_PURCHASE_BUNDLE_FOR_GOLD_MESSAGE = 'lsPurchaseBundleForGold'
    _SM_TYPE_BATTLE_RESULT = 'lsBattleResults'
    _SM_TYPE_BATTLE_PASS_POINTS_MESSAGE = 'lsBattlePassPointsMessage'
    _SM_TYPE_AUTO_MAINTENANCE = 'lsAutoMaintenance'
    _SM_TYPE_LS_INVOICE_RECEIVED = 'lsInvoiceReceived'
    _FAIRPLAY_VEHICLE_BATTLE_STATS_COMPONENT = 'LSFairplayVehicleBattleStatsComponent'
    _SM_TYPES = [_SM_TYPE_ARTEFACT_REWARD_CONGRATS,
     _SM_TYPE_DIFFICULTY_REWARD_CONGRATS,
     _SM_TYPE_ARTEFACT_KEYS_MESSAGE,
     _SM_TYPE_BATTLE_RESULT,
     _SM_TYPE_AUTO_MAINTENANCE,
     _SM_TYPE_LS_INVOICE_RECEIVED]
    _CLIENT_SM_TYPES = [_SM_TYPE_PURCHASE_BUNDLE_FOR_GOLD_MESSAGE, _SM_TYPE_DIFFICULTY_OPEN_MESSAGE, _SM_TYPE_BATTLE_PASS_POINTS_MESSAGE]

    @property
    def _rosterClass(self):
        from last_stand_common.last_stand_roster_config import LastStandRoster
        return LastStandRoster

    @property
    def _client_attackReasonToCode(self):
        return {ATTACK_REASON.getIndex(ATTACK_REASON.LS_ABILITY_VAMPIRE): 'DEATH_FROM_SHOT',
         ATTACK_REASON.getIndex(ATTACK_REASON.LS_ABILITY_AOE_DAMAGE): 'DEATH_FROM_SHOT',
         ATTACK_REASON.getIndex(ATTACK_REASON.LS_SHOT_AOE_DAMAGE): 'DEATH_FROM_SHOT',
         ATTACK_REASON.getIndex(ATTACK_REASON.LS_SHOT_AOE_DRAIN_ENEMY_HP): 'DEATH_FROM_SHOT',
         ATTACK_REASON.getIndex(ATTACK_REASON.LS_SHOT_AOE_STUN): 'DEATH_FROM_SHOT',
         ATTACK_REASON.getIndex(ATTACK_REASON.LS_BOMBER_EXPLOSION): 'DEATH_FROM_LS_BOMBER_EXPLOSION',
         ATTACK_REASON.getIndex(ATTACK_REASON.LS_DEATH_PIT): 'DEATH_FROM_LS_DEATH_PIT',
         ATTACK_REASON.getIndex(ATTACK_REASON.LS_PHASE_TIMER): 'DEATH_FROM_LS_PHASE_TIMER',
         ATTACK_REASON.getIndex(ATTACK_REASON.LS_LEAVER): 'DEATH_FROM_LS_PHASE_TIMER',
         ATTACK_REASON.getIndex(ATTACK_REASON.LS_EXTRA_DAMAGE_SITUATIONAL): 'DEATH_FROM_SHOT'}


def registerLoggingParams(personality):
    from server_constants import BONUSES_WITH_HEATMAPS
    BONUSES_WITH_HEATMAPS.update({'last_stand': (constants.ARENA_BONUS_MASK.TYPE_BITS[ARENA_BONUS_TYPE.LAST_STAND], False),
     'last_stand_medium': (constants.ARENA_BONUS_MASK.TYPE_BITS[ARENA_BONUS_TYPE.LAST_STAND_MEDIUM], False),
     'last_stand_hard': (constants.ARENA_BONUS_MASK.TYPE_BITS[ARENA_BONUS_TYPE.LAST_STAND_HARD], False)})


CURRENT_QUEUE_TYPE_KEY = 'currentQueueType'

class DifficultyLevelToken(object):
    EASY = 'ls_difficulty_level:easy'
    MEDIUM = 'ls_difficulty_level:medium'
    HARD = 'ls_difficulty_level:hard'
    ALWAYS_AVIABLED = (EASY,)
    ACCESS_REQUIRED = (MEDIUM, HARD)
    ALL_LEVELS = (EASY, MEDIUM, HARD)


TOKEN_DIFFICULTY_LEVEL_TO_QUEUE_TYPE = {DifficultyLevelToken.EASY: QUEUE_TYPE.LAST_STAND,
 DifficultyLevelToken.MEDIUM: QUEUE_TYPE.LAST_STAND_MEDIUM,
 DifficultyLevelToken.HARD: QUEUE_TYPE.LAST_STAND_HARD}
QUEUE_TYPE_TO_TOKEN_DIFFICULTY_LEVEL = {QUEUE_TYPE.LAST_STAND: DifficultyLevelToken.EASY,
 QUEUE_TYPE.LAST_STAND_MEDIUM: DifficultyLevelToken.MEDIUM,
 QUEUE_TYPE.LAST_STAND_HARD: DifficultyLevelToken.HARD}
ARENA_BONUS_TYPE_TO_LEVEL = {ARENA_BONUS_TYPE.LAST_STAND: 1,
 ARENA_BONUS_TYPE.LAST_STAND_MEDIUM: 2,
 ARENA_BONUS_TYPE.LAST_STAND_HARD: 3}

class ShopSettings(object):
    SHOP_BUNDLE_PREFFIX = 'ls2_0bundle'
    PURCHASED_SUFFIX = ':purchased'
    WG_MONEY_CALLBACK = 'lsPurchaseEventShopBundleWGMoney'


class ArtefactsSettings(object):
    ARTEFACT = 'ls_artefact'
    QUEST_PREFIX = 'ls_artefact:'
    TOKEN_PREFIX = 'ls_artefact:'
    KEY_TOKEN = 'ls_artefact:key'
    KEY_NOTIFY_TOKEN = 'ls_artefact:notifyKey'
    KEY_TOKEN_TTL = 2160
    KEY_TOKEN_LIMIT = 10000


class DifficultyMissionsSettings(object):
    DIFFICULTY_MISSISONS_QUEST_PREFFIX = 'ls_difficulty_missions:'
    DIFFICULTY_MISSISONS_QUEST_TPL = 'ls_difficulty_missions:{difficulty}:{index}'


class ArtefactType(object):
    TEXT = 'text'
    SOUND = 'sound'
    FINAL = 'final'
    KING_REWARD = 'kingReward'


ARTEFACT_ID_MASK = 'ls_artefact:{index}:'

class DailyMissionsSettings(object):
    DAILY_MISSION_QUEST_PREFIX = 'ls_daily_mission:'
    BADGE_MISSION_QUEST = 'ls_badge:mission'


class LSSoulsChangeReason(object):
    CHEAT = 0
    COLLECTOR = 1
    PICK_UP = 3
    VEHICLE_DEATH = 5
    COLLECTOR_RESET = 6
    EQUIPMENT_USED = 7
    PHASE_PROGRESS = 8
    PHASE_START = 9


class LSBuffSequenceVisibilityMode(enum.IntEnum):
    NONE = 0
    SELF = 1
    OTHERS = 2
    ALL = 3


class BATTLE_EVENT_TYPE(BET, ConstInjector):
    LS_GAMEPLAY_ACTION = 102


class LSMarkersType(object):
    CAMP = 'LS_CAMP'
    MAGNUS = 'LS_MAGNUS'


class LSMarkerComponentNames(object):
    CAMP = 'lsCampMarker'
    MAGNUS = 'lsMagnusMarker'
    ALL = (CAMP, MAGNUS)


class DamageResistanceReason(constants.DamageResistanceReason, ConstInjector):
    LS_NITRO = 105
    LS_DAMAGE_SHIELD = 106
    LS_MODULES_INVULNERABILITY_BUFF = 107


class LSRepairReason(object):
    NONE = 0
    BASIC_REPAIR = 1
    REPAIR_BY_AOE_ABILITY_VAMPIRE = 2
    REPAIR_BY_PASSIVE_VAMPIRE = 3
    REPAIR_BY_INFINITE_REGENERATION = 4
    REPAIR_BY_AOE_TEAM_REPAIR_KIT = 5
    REPAIR_BY_SELF_SITUATIONAL = 6


LS_CHAT_CHANNEL = '#last_stand.last_stand_chat:channels/last_stand'
LS_INVENTORY_PDATA_KEY = 'LS_inventory'
LS_INFO_PDATA_KEY = 'LS_info'
LS_EMPTY_SLOTS_EQ = ('LS_emptySlot0', 'LS_emptySlot1', 'LS_emptySlot2')
LS_BUILT_IN_EQUIPMENT = []
LS_DEFAULT_AUTO_MAINTENANCE = True
LS_VEHILCE_DAILY_QUEST = 'ls_vehicle_daily_quest:keys'
INVALID_PHASE = 0
ARENA_SYNC_WATCHER_DEFAULT = True
ARENA_SYNC_WATCHER_NAME_FMT = 'arenaPool/matchmaker/%s/isArenaSyncEnabled'

class ArenaSyncWatchers(object):
    EASY = ARENA_SYNC_WATCHER_NAME_FMT % 'last_stand'
    MEDIUM = ARENA_SYNC_WATCHER_NAME_FMT % 'last_stand_medium'
    HARD = ARENA_SYNC_WATCHER_NAME_FMT % 'last_stand_hard'
    ALL = (EASY, MEDIUM, HARD)
