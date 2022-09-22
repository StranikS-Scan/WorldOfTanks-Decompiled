# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/br_constants.py
from constants import ARENA_BONUS_TYPE
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from shared_utils import CONST_CONTAINER

class PersonalEfficiency(CONST_CONTAINER):
    SPOTTED = 'spotted'
    KILLS = 'kills'
    STUN = 'damageAssistedStun'
    DAMAGE = 'damageDealt'
    ARMOR = 'damageBlockedByArmor'
    ASSIST = 'damageAssisted'
    CRITS = 'critsCount'
    ALL = (STUN,
     SPOTTED,
     ASSIST,
     ARMOR,
     CRITS,
     DAMAGE,
     KILLS)


class EfficiencyKeys(CONST_CONTAINER):
    ENEMY_PARAM_NAME = 'enemyParamName'
    TOTAL = 'summ'
    ICON = 'icon'
    TYPE = 'effType'


class PremiumXpBonusRestrictions(CONST_CONTAINER):
    NO_RESTRICTION = 0
    IS_APPLIED = 1
    IS_LOST_BATTLE = 2
    IS_BONUS_DISABLED = 3
    IS_BLOCKED_BY_VEHICLE = 4
    IS_BLOCKED_BY_CREW = 5
    IS_XP_TO_TMEN_DISABLED = 6
    IS_XP_TO_TMEN_ENABLED = 7


class PremiumBenefitSubstitutionIDs(CONST_CONTAINER):
    MULTIPLIER_PERCENT = 'multiplier_percent'
    MULTIPLIER = 'multiplier'
    COUNT = 'count'


EfficiencyItems = {PersonalEfficiency.SPOTTED: {EfficiencyKeys.TOTAL: 'summSpotted',
                              EfficiencyKeys.ENEMY_PARAM_NAME: 'spotted',
                              EfficiencyKeys.TYPE: BATTLE_EFFICIENCY_TYPES.DETECTION},
 PersonalEfficiency.ASSIST: {EfficiencyKeys.TOTAL: 'summAssist',
                             EfficiencyKeys.ENEMY_PARAM_NAME: 'damageAssisted',
                             EfficiencyKeys.TYPE: BATTLE_EFFICIENCY_TYPES.ASSIST},
 PersonalEfficiency.ARMOR: {EfficiencyKeys.TOTAL: 'summArmor',
                            EfficiencyKeys.ENEMY_PARAM_NAME: 'damageBlockedByArmor',
                            EfficiencyKeys.TYPE: BATTLE_EFFICIENCY_TYPES.ARMOR},
 PersonalEfficiency.DAMAGE: {EfficiencyKeys.TOTAL: 'summDamage',
                             EfficiencyKeys.ENEMY_PARAM_NAME: 'damageDealt',
                             EfficiencyKeys.TYPE: BATTLE_EFFICIENCY_TYPES.DAMAGE},
 PersonalEfficiency.KILLS: {EfficiencyKeys.TOTAL: 'summKill',
                            EfficiencyKeys.ENEMY_PARAM_NAME: 'targetKills',
                            EfficiencyKeys.TYPE: BATTLE_EFFICIENCY_TYPES.DESTRUCTION},
 PersonalEfficiency.STUN: {EfficiencyKeys.TOTAL: 'summStun',
                           EfficiencyKeys.ENEMY_PARAM_NAME: 'damageAssistedStun',
                           EfficiencyKeys.TYPE: BATTLE_EFFICIENCY_TYPES.ASSIST_STUN},
 PersonalEfficiency.CRITS: {EfficiencyKeys.TOTAL: 'summCrits',
                            EfficiencyKeys.ENEMY_PARAM_NAME: 'critsCount',
                            EfficiencyKeys.TYPE: BATTLE_EFFICIENCY_TYPES.CRITS}}
STAT_STUN_FIELD_NAMES = ('damageAssistedStun', 'stunNum', 'stunDuration')
COMMON_STATS_ITEMS_TO_PERSONAL = {'damageAssisted': 'damageAssistedSelf',
 'damageAssistedStun': 'damageAssistedStunSelf'}
MAX_TEAM_RANK = 3
UNKNOWN_ACHIEVEMENT_ID = -1

class BattleResultsRecord(CONST_CONTAINER):
    ARENA_UNIQUE_ID = 'arenaUniqueID'
    COMMON = 'common'
    PERSONAL = 'personal'
    PLAYERS = 'players'
    VEHICLES = 'vehicles'
    AVATARS = 'avatars'
    TOP_LEVEL_RECORDS = (COMMON,
     PERSONAL,
     PLAYERS,
     VEHICLES,
     AVATARS)
    PERSONAL_AVATAR = 'avatar'
    COMMON_BOTS = 'bots'


class PremiumState(CONST_CONTAINER):
    NONE = 0
    HAS_ALREADY = 1
    BUY_ENABLED = 2
    BOUGHT = 4


class ProgressAction(CONST_CONTAINER):
    RESEARCH_UNLOCK_TYPE = 'UNLOCK_LINK_TYPE'
    PURCHASE_UNLOCK_TYPE = 'PURCHASE_LINK_TYPE'
    NEW_SKILL_UNLOCK_TYPE = 'NEW_SKILL_LINK_TYPE'


class PlayerTeamResult(CONST_CONTAINER):
    WIN = 'win'
    DEFEAT = 'lose'
    DRAW = 'tie'
    ENDED = 'ended'


class FactorValue(CONST_CONTAINER):
    BASE_CREDITS_FACTOR = 100
    PREMUIM_CREDITS_FACTOR = 150
    PREMUIM_PLUS_CREDITS_FACTOR = 150
    BASE_XP_FACTOR = 100
    PREMUIM_XP_FACTOR = 150
    PREMUIM_PLUS_XP_FACTOR = 150
    ADDITIONAL_BONUS_ZERO_FACTOR = 0
    ADDITIONAL_BONUS_ONE_FACTOR = 10


class EmblemType(CONST_CONTAINER):
    CLAN = 1


class UIVisibility(CONST_CONTAINER):
    SHOW_SQUAD = 1
    SHOW_RESOURCES = 2


POSTBATTLE20_ARENAS = frozenset([ARENA_BONUS_TYPE.EVENT_BATTLES, ARENA_BONUS_TYPE.EVENT_BATTLES_2])
ARENAS_WITH_PREMIUM_BONUSES = frozenset([ARENA_BONUS_TYPE.REGULAR, ARENA_BONUS_TYPE.EPIC_RANDOM, ARENA_BONUS_TYPE.RANKED])
