# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/common/armory_yard_constants.py
from enum import Enum
CMD_COLLECT_REWARDS = 31002
CMD_BUY_STEP_TOKENS = 31003
CMD_CLAIM_FINAL_REWARD = 31004
DEV_CMD_ADD_TOKEN_S = 31005
DEV_CMD_SET_CYCLE = 31009
DEV_CMD_SET_QUEST = 31010
CMD_BUY_SHOP_PRODUCT = 31014
DEV_CMD_ADD_ARMORY_COIN = 31015
DAY_BEFORE_END_STYLE_QUEST = 2
MAX_PAID_TOKENS = 99
ARMORY_YARD_COIN_NAME = 'armory_coin'
PDATA_KEY_ARMORY_YARD = 'armoryYard'
FEATURE_NAME_BASE = 'armory_yard'
STAGE_TOKEN_POSTFIX = 'C'
BATTLE_TOKEN_POSTFIX = 'B'
CURRENCY_TOKEN_POSTFIX = 'S'
END_TOKEN_POSTFIX = 'end'
POST_PROGRESSION_PAID_TOKEN_POSTFIX = 'paid'
END_QUEST_POSTFIX = 'end'
CONVERTER_QUEST_POSTFIX = 'converter'
PROGRESSION_LEVEL_PDATA_KEY = 'progressionLevel'
CLAIMED_FINAL_REWARD = 'claimedFinalReward'
SHOP_PDATA_KEY = 'shop'
SHOP_LAST_SEASON_COMPLETED = 'isLastSeasonCompleted'
SHOP_PRODUCT_LIMITS = 'limits'
POSTBATTLE_QUEST = 'postBattle'
INTRO_VIDEO = None
STYLE_QUEST_POSTFIX = 'style'
VEHICLE_NAME = 'ussr:R75_SU122_54'
AY_VIDEOS = ('ay_ep3_armour.usm', 'ay_ep3_tracks.usm', 'ay_ep3_gun.usm', 'ay_ep3_turret.usm')

class State(Enum):
    BEFOREPROGRESSION = 'beforeProgression'
    ACTIVE = 'active'
    POSTPROGRESSION = 'postProgression'
    COMPLETED = 'completed'
    DISABLED = 'disabled'


DISABLED_STATES = (State.DISABLED, State.BEFOREPROGRESSION)

def getStageToken(cycleID):
    return ':'.join((FEATURE_NAME_BASE, 'cycle_{}'.format(cycleID), STAGE_TOKEN_POSTFIX))


def getCurrencyToken(seasonID):
    return ':'.join((FEATURE_NAME_BASE, 'season_{}'.format(seasonID), CURRENCY_TOKEN_POSTFIX))


def getEndToken(cycleID):
    return ':'.join((FEATURE_NAME_BASE, 'cycle_{}'.format(cycleID), END_TOKEN_POSTFIX))


def getPostProgressionPaidEntitlement(seasonID):
    return ':'.join((FEATURE_NAME_BASE, 'season_{}'.format(seasonID), POST_PROGRESSION_PAID_TOKEN_POSTFIX))


def getGroupName(cycleID):
    return '_'.join((FEATURE_NAME_BASE, 'cycle_{}'.format(cycleID)))


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


def isArmoryYardStyleQuest(questId):
    return questId.startswith(FEATURE_NAME_BASE) and questId.endswith(STYLE_QUEST_POSTFIX)


def armoryInitialData():
    return {'currentSeason': None,
     CLAIMED_FINAL_REWARD: False,
     PROGRESSION_LEVEL_PDATA_KEY: 0,
     SHOP_PDATA_KEY: {'limits': {},
                      SHOP_LAST_SEASON_COMPLETED: False}}
