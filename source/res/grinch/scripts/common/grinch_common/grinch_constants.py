# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/common/grinch_common/grinch_constants.py
from collections import namedtuple
import enum
import UnitBase
import arena_bonus_type_caps
import constants
from constants_utils import ConstInjector
from BattleFeedbackCommon import BATTLE_EVENT_TYPE as BET

class GrinchAbilities(object):
    GRINCH_REPAIR_KIT = 'builtinGrinchRepairkit'
    GRINCH_TURRET = 'builtinGrinchTurret'
    GRINCH_HEAL = 'builtinGrinchHeal'
    GRINCH_BLIZZARD = 'builtinGrinchBlizzard'
    GRINCH_RAGE = 'builtinGrinchRage'
    GRINCH_FLARE = 'builtinGrinchFlare'
    GRINCH_STEALTH = 'builtinGrinchStealth'


class GrinchShells(object):
    SHELL_ASSAULT = '_152mm_AP_T_grinch'
    SHELL_CARRIER = '_105mm_OFL_105_D1504_grinch'
    SHELL_SUPPORT = '_105mm_AP_DM13_grinch'


class ARENA_GUI_TYPE(constants.ARENA_GUI_TYPE, ConstInjector):
    GRINCH = 106


class ARENA_BONUS_TYPE_CAPS(arena_bonus_type_caps.ARENA_BONUS_TYPE_CAPS, ConstInjector):
    _const_type = str
    GRINCH = 'GRINCH'


class ARENA_BONUS_TYPE(constants.ARENA_BONUS_TYPE, ConstInjector):
    GRINCH = 106


class QUEUE_TYPE(constants.QUEUE_TYPE, ConstInjector):
    GRINCH = 106


class PREBATTLE_TYPE(constants.PREBATTLE_TYPE, ConstInjector):
    GRINCH = 106


class UNIT_MGR_FLAGS(UnitBase.UNIT_MGR_FLAGS, ConstInjector):
    GRINCH = 524288


class ROSTER_TYPE(UnitBase.ROSTER_TYPE, ConstInjector):
    GRINCH = UNIT_MGR_FLAGS.SQUAD | UNIT_MGR_FLAGS.GRINCH


class INVITATION_TYPE(constants.INVITATION_TYPE, ConstInjector):
    GRINCH = PREBATTLE_TYPE.GRINCH


class ATTACK_REASON(constants.ATTACK_REASON, ConstInjector):
    _const_type = str
    REDIRECTED_DAMAGE = 'redirected_damage_from_bot'
    SLAVE_BOT_DAMAGED = 'slave_bot_damaged'
    BLIZZARD_ABILITY = 'damage_by_blizzard_ability'
    SNOWSTORM = 'damage_by_snowstorm'
    BASE_DEFENDER_BONUS = 'base_defender_bonus'
    ABILITY_ASSIST_FLARE = 'ability_assist_flare'
    ABILITY_ASSIST_BLIZZARD = 'ability_assist_blizzard'
    ABILITY_ASSIST_BUFF = 'ability_assist_buff'
    RAGE = 'rage'


DAMAGE_INFO_CODES_PER_ATTACK_REASON = {ATTACK_REASON.BLIZZARD_ABILITY: 'DEATH_FROM_ABILITIES',
 ATTACK_REASON.SNOWSTORM: 'DEATH_FROM_ABILITIES',
 ATTACK_REASON.RAGE: 'DEATH_FROM_ABILITIES'}
BATTLE_FEEDBACK_REASONS_AFTER_DEATH = {ATTACK_REASON.ABILITY_ASSIST_BUFF,
 ATTACK_REASON.ABILITY_ASSIST_FLARE,
 ATTACK_REASON.ABILITY_ASSIST_BLIZZARD,
 ATTACK_REASON.REDIRECTED_DAMAGE,
 ATTACK_REASON.SLAVE_BOT_DAMAGED}

class GameSeasonType(constants.GameSeasonType, ConstInjector):
    GRINCH = 106


class CLIENT_UNIT_CMD(UnitBase.CLIENT_UNIT_CMD, ConstInjector):
    pass


class StatsActions(enum.Enum):
    DAMAGE = 'damage'
    RAMMING = 'ramming'
    HIT_ASSIST = 'hitAssist'
    ABILITY_ASSIST_FLARE = 'abilityAssistFlare'
    ABILITY_ASSIST_BLIZZARD = 'abilityAssistBlizzard'
    ABILITY_ASSIST_BUFF = 'abilityAssistBuff'
    KILL = 'kill'
    BASE_DEFENDER_BONUS = 'baseDefenderBonus'
    ENEMY_DETECTION = 'enemyDetection'
    PRESENTS_DELIVERY = 'presentsDelivery'
    PRESENTS_THEFT = 'presentsTheft'
    PRESENTS_STEALTH_THEFT = 'presentsStealthTheft'
    PRESENT_CARRIER_KILLED = 'carrierKilled'
    TURRET_DAMAGE = 'turretDamage'
    RAGE_DAMAGE = 'rageDamage'
    STEALTH_DAMAGE = 'stealth_damage'
    HEAL = 'heal'
    FROZEN_KILL = 'frozenKill'
    CLOSE_RANGE_DAMAGE = 'closeRangeDamage'
    FLARED_DAMAGE = 'flaredDamage'


ACTIONS_AWARDING_PROGRESS_POINTS = (StatsActions.DAMAGE,
 StatsActions.HIT_ASSIST,
 StatsActions.ABILITY_ASSIST_FLARE,
 StatsActions.KILL,
 StatsActions.BASE_DEFENDER_BONUS,
 StatsActions.ENEMY_DETECTION,
 StatsActions.PRESENTS_DELIVERY,
 StatsActions.ABILITY_ASSIST_BLIZZARD,
 StatsActions.ABILITY_ASSIST_BUFF)
BattleEventTypeInfo = namedtuple('BattleEventTypeInfo', ('battleEventType', 'attackReason'))
STATS_ACTION_TO_BET_INFO = {StatsActions.PRESENTS_DELIVERY: BattleEventTypeInfo(BET.BASE_CAPTURE_DROPPED, None),
 StatsActions.ABILITY_ASSIST_FLARE: BattleEventTypeInfo(BET.DAMAGE, ATTACK_REASON.ABILITY_ASSIST_FLARE),
 StatsActions.ABILITY_ASSIST_BLIZZARD: BattleEventTypeInfo(BET.DAMAGE, ATTACK_REASON.ABILITY_ASSIST_BLIZZARD),
 StatsActions.ABILITY_ASSIST_BUFF: BattleEventTypeInfo(BET.DAMAGE, ATTACK_REASON.ABILITY_ASSIST_BUFF),
 StatsActions.BASE_DEFENDER_BONUS: BattleEventTypeInfo(BET.DAMAGE, ATTACK_REASON.BASE_DEFENDER_BONUS)}

class GrinchClientArenaComponents(object):
    GRINCH_VISUAL_STATE_GO_STORAGE = 'grinchVisualStateGOStorage'


class Configs(enum.Enum):
    GRINCH_CONFIG = 'grinch_config'


class EventStates(enum.Enum):
    START = 0
    BATTLES_FINISH = 1
    SUSPEND = 2
    RESUME = 3
    BATTLES_CHAPTER_BEGIN = 4
    BATTLES_CHAPTER_FINISH = 5


class Teams(enum.IntEnum):
    CYAN = 1
    YELL = 2
    MGNT = 3
    BOTS = 4


PLAYER_TEAMS = (Teams.CYAN, Teams.YELL, Teams.MGNT)
PLAYER_VEHICLE_TYPES = ('lightTank', 'mediumTank', 'heavyTank')
TURRET_SPHERE_COLLIDER_RADIUS = 3

class GrinchModeSelectorRewardID(enum.Enum):
    ATTACHMENT_3D = 'attachment3D'
    STYLE_2D = 'style2D'
