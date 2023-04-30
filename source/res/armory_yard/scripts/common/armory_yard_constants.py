# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/common/armory_yard_constants.py
from enum import Enum
CMD_COLLECT_REWARDS = 31002
CMD_BUY_STEP_TOKENS = 31003
CMD_CLAIM_FINAL_REWARD = 31004
DEV_CMD_ADD_TOKEN_S = 31005
MAX_TOKEN_AT_CHAPTER = 6
DAY_BEFORE_END_STYLE_QUEST = 2
PDATA_KEY_ARMORY_YARD = 'armoryYard'
FEATURE_NAME_BASE = 'armory_yard'
STAGE_TOKEN_POSTFIX = 'B'
CURRENCY_TOKEN_POSTFIX = 'S'
END_TOKEN_POSTFIX = 'end'
END_QUEST_POSTFIX = 'end'
CONVERTER_QUEST_POSTFIX = 'converter'
PROGRESSION_LEVEL_PDATA_KEY = 'progressionLevel'
CLAIMED_FINAL_REWARD = 'claimedFinalReward'
POSTBATTLE_QUEST = 'postBattle'
INTO_VIDEO = 'ay_intro'
STYLE_QUEST_POSTFIX = 'style'
VEHICLE_NAME = 'ussr:R208_Object_156O'
AY_VIDEOS = ['ay_armour.usm',
 'ay_intro.usm',
 'ay_reward.usm',
 'ay_tracks.usm']

class State(Enum):
    BEFOREPROGRESSION = 'beforeProgression'
    ACTIVE = 'active'
    ACTIVELASTHOURS = 'activeLastHours'
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


def getGroupName(cycleID):
    return '_'.join((FEATURE_NAME_BASE, 'cycle_{}'.format(cycleID)))


def getConverterQuestID(cycleID):
    return '_'.join((FEATURE_NAME_BASE, 'cycle_{}'.format(cycleID), CONVERTER_QUEST_POSTFIX))


def getEndQuestID(cycleID):
    return '_'.join((FEATURE_NAME_BASE, 'cycle_{}'.format(cycleID), END_QUEST_POSTFIX))


def isArmoryYardCurrencyToken(tokenID):
    return tokenID.startswith(FEATURE_NAME_BASE) and tokenID.endswith(CURRENCY_TOKEN_POSTFIX)


def isArmoryYardStyleQuest(questId):
    return questId.startswith(FEATURE_NAME_BASE) and questId.endswith(STYLE_QUEST_POSTFIX)


def armoryInitialData():
    return {'currentSeason': None,
     CLAIMED_FINAL_REWARD: False,
     PROGRESSION_LEVEL_PDATA_KEY: 0}
