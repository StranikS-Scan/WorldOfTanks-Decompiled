# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/common/armory_yard_constants.py
from enum import Enum
CMD_COLLECT_REWARDS = 31002
CMD_BUY_STEP_TOKENS = 31003
CMD_CLAIM_RARE_REWARD = 31004
DEV_CMD_ADD_PROGRESSION_TOKEN = 31005
DEV_CMD_SET_CYCLE = 31009
DEV_CMD_SET_QUEST = 31010
CMD_BUY_SHOP_PRODUCT = 31014
DEV_CMD_ADD_ARMORY_COIN = 31015
CMD_REROLL_ARMORY_QUEST = 31029
CMD_ACCEPT_REROLL_ARMORY_QUEST = 31030
DAY_BEFORE_END_STYLE_QUEST = 2
MAX_BUNDLE_TOKENS = 99
PDATA_KEY_ARMORY_YARD = 'armoryYard'
ARMORY_YARD_COIN_NAME = 'armory_coin'
FEATURE_NAME_BASE = 'armory_yard'
STAGE_TOKEN_POSTFIX = 'C'
BATTLE_TOKEN_POSTFIX = 'B'
BATTLE_POST_PROGRESSION_TOKEN_POSTFIX = 'Bp'
PROGRESSION_TOKEN_POSTFIX = 'progression'
POST_PROGRESSION_TOKEN_POSTFIX = 'post_progression'
SUBTRAHEND_STAGE_TOKEN_POSTFIX = 'D'
END_TOKEN_POSTFIX = 'end'
PURCHASE_STAGE_ENT_POSTFIX = 'paid'
END_QUEST_POSTFIX = 'end'
CONVERTER_QUEST_POSTFIX = 'converter'
FREE_REROLL_POSTFIX = 'free_reroll'
DAILY_FREE_REROLLED_POSTFIX = 'daily_free_rerolled'
PROGRESSION_LEVEL_PDATA_KEY = 'progressionLevel'
CLAIMED_FINAL_REWARD = 'claimedFinalReward'
CLAIMED_PROGRESSION_REWARD = 'claimedProgressionReward'
CLAIMED_POST_PROGRESSION_REWARD = 'claimedPostProgressionReward'
SHOP_PDATA_KEY = 'shop'
SHOP_LAST_SEASON_COMPLETED = 'isLastSeasonCompleted'
SHOP_PRODUCT_LIMITS = 'limits'
QUEST_CONDITION_OVERRIDE_PDATA_KEY = 'questConditionsOverride'
CURRENT_REROLL_PDATA_KEY = 'currentReroll'
LAST_SUGGESTED_CONDITIONS = 'lastSuggestedConditions'
NEED_CLEAR_REROLL_PROGRESS = 'clearReroll'
POSTBATTLE_QUEST = 'postBattle'
INTRO_VIDEO = None
STYLE_QUEST_POSTFIX = 'style'
VEHICLE_NAME = 'ussr:R75_SU122_54'
POST_PROGRESSION_SHORT_NAME = 'post_prog'

class State(Enum):
    BEFOREPROGRESSION = 'beforeProgression'
    ACTIVE = 'active'
    PURCHASESTAGE = 'purchaseStage'
    COMPLETED = 'completed'
    DISABLED = 'disabled'
    NOTREPLACED = 'notReplaced'


DISABLED_STATES = (State.DISABLED, State.BEFOREPROGRESSION)

def getStageToken(cycleID):
    return ':'.join((FEATURE_NAME_BASE, 'cycle_{}'.format(cycleID), STAGE_TOKEN_POSTFIX))


def getSubtrahendStageToken(seasonID):
    return ':'.join((FEATURE_NAME_BASE, 'season_{}'.format(seasonID), SUBTRAHEND_STAGE_TOKEN_POSTFIX))


def getProgressionToken(seasonID):
    return ':'.join((FEATURE_NAME_BASE, 'season_{}'.format(seasonID), PROGRESSION_TOKEN_POSTFIX))


def getPostProgressionToken(seasonID):
    return ':'.join((FEATURE_NAME_BASE, 'season_{}'.format(seasonID), POST_PROGRESSION_TOKEN_POSTFIX))


def getBattleToken(cycleID):
    return ':'.join((FEATURE_NAME_BASE, 'cycle_{}'.format(cycleID), BATTLE_TOKEN_POSTFIX))


def getBattlePostProgressionToken(seasonID):
    return ':'.join((FEATURE_NAME_BASE, 'season_{}'.format(seasonID), BATTLE_POST_PROGRESSION_TOKEN_POSTFIX))


def getFreeRerollToken(groupName):
    return ':'.join((groupName, FREE_REROLL_POSTFIX))


def getDailyUserFreeRerolledToken(groupName):
    return ':'.join((groupName, DAILY_FREE_REROLLED_POSTFIX))


def getEndToken(cycleID):
    return ':'.join((FEATURE_NAME_BASE, 'cycle_{}'.format(cycleID), END_TOKEN_POSTFIX))


def getPurchaseStagePaidEntitlement(seasonID):
    return ':'.join((FEATURE_NAME_BASE, 'season_{}'.format(seasonID), PURCHASE_STAGE_ENT_POSTFIX))


def getGroupName(cycleID):
    return '_'.join((FEATURE_NAME_BASE, 'cycle_{}'.format(cycleID)))


POST_PROGRESSION_GROUP_PREFIX = FEATURE_NAME_BASE + '_' + POST_PROGRESSION_SHORT_NAME
_POST_PROGRESSION_GROUP_TEMPLATE = POST_PROGRESSION_GROUP_PREFIX + '_{}'

def getPostProgressionGroupName(seasonID):
    return _POST_PROGRESSION_GROUP_TEMPLATE.format(seasonID)


def getEndQuestID(cycleID):
    return '_'.join((FEATURE_NAME_BASE, 'cycle_{}'.format(cycleID), END_QUEST_POSTFIX))


def getBundleBlockToken(seasonID):
    return '{}_starter_pack:season_{}'.format(FEATURE_NAME_BASE, seasonID)


def getFinalEndQuestID(seasonID):
    return '_'.join((FEATURE_NAME_BASE, 'season_{}'.format(seasonID), END_QUEST_POSTFIX))


def isArmoryYardToken(tokenID):
    return tokenID.startswith(FEATURE_NAME_BASE)


def isArmoryYardBattleToken(tokenID):
    return tokenID.startswith(FEATURE_NAME_BASE) and tokenID.endswith(BATTLE_TOKEN_POSTFIX)


def isArmoryYardCycleToken(tokenID):
    return tokenID.startswith(FEATURE_NAME_BASE) and tokenID.endswith(STAGE_TOKEN_POSTFIX)


def isArmoryYardStyleQuest(questId):
    return questId.startswith(FEATURE_NAME_BASE) and questId.endswith(STYLE_QUEST_POSTFIX)


def armoryInitialData():
    return {'currentSeason': None,
     CLAIMED_PROGRESSION_REWARD: False,
     CLAIMED_POST_PROGRESSION_REWARD: False,
     PROGRESSION_LEVEL_PDATA_KEY: 0,
     SHOP_PDATA_KEY: {'limits': {},
                      SHOP_LAST_SEASON_COMPLETED: False},
     QUEST_CONDITION_OVERRIDE_PDATA_KEY: {},
     LAST_SUGGESTED_CONDITIONS: [],
     CURRENT_REROLL_PDATA_KEY: {}}


TEMP_TOKENS_LIFETIME_IN_HOURS = 240
COMPLETED_CONDITION_POSTFIX = 'completed'
ARMORY_YARD_QUEST_PREFIX = 'armory_yard_cycle'
CONDITION_PREFIX = 'armory_yard_condition'
NEED_TOKEN_QUEST_COMPLETE_POSTFIX = 'nc'

def getConditionToken(conditionID):
    return 'armory_yard_condition:{}'.format(conditionID)


def getConditionCompletedToken(conditionID):
    return 'armory_yard_condition:{}:completed'.format(conditionID)


def getConditionIDByToken(token):
    return int(token.split(':')[1])


def getConditionTokenByQuestID(questID):
    return questID.rsplit(':', 1)[0]


def getConditionIDByQuestID(questID):
    return int(questID.split(':')[1])


def getQuestCompletedToken(questID):
    return '{}:{}'.format(questID, NEED_TOKEN_QUEST_COMPLETE_POSTFIX)


ARMORY_YARD_SYS_MSG_PROGRESSION = 'ay_progression'
ARMORY_YARD_SYS_MSG_POST_PROGRESSION = 'ay_post_progression'
TOKEN_EXTRA_TIME_TO_LIVE = 4320
