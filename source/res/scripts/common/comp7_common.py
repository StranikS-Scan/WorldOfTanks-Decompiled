# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/comp7_common.py
import enum
ROLE_EQUIPMENT_TAG = 'roleEquipment'
COMP7_QUEST_PREFIX = 'comp7_2023_1'
COMP7_QUEST_DELIMITER = '_'
COMP7_TOKEN_WEEKLY_REWARD_NAME = 'comp7_2023_1_weekly_rewards_token'

@enum.unique
class Comp7QuestType(enum.Enum):
    RANKS = 'ranks'
    TOKENS = 'token'
    PERIODIC = 'period'
    ACTIVITY = 'activity'
    WEEKLY = 'weekly'


CLIENT_VISIBLE_QUESTS_TYPE = (Comp7QuestType.TOKENS,
 Comp7QuestType.RANKS,
 Comp7QuestType.PERIODIC,
 Comp7QuestType.WEEKLY)
