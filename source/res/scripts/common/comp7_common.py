# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/comp7_common.py
import enum
ROLE_EQUIPMENT_TAG = 'roleEquipment'
COMP7_QUEST_PREFIX = 'comp7'
COMP7_QUEST_DELIMITER = '_'

@enum.unique
class Comp7QuestType(enum.Enum):
    RANKS = 'ranks'
    WINS = 'wins'
    PERIODIC = 'period'
    ACTIVITY = 'activity'


CLIENT_VISIBLE_QUESTS_TYPE = (Comp7QuestType.WINS, Comp7QuestType.RANKS, Comp7QuestType.PERIODIC)
