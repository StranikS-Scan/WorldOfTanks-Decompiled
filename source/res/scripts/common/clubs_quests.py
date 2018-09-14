# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/clubs_quests.py
import os
from pprint import pformat
from quest_cache_helpers import readQuestsFromFile
from constants import ITEM_DEFS_PATH, EVENT_TYPE, CURRENT_REALM
from debug_utils import LOG_DEBUG_DEV
_CLUBS_QUESTS_DIR = ITEM_DEFS_PATH + 'clubs_quests/'
_LADDER_QUESTS_FILE = 'ladder_quests_%s.xml' % CURRENT_REALM.upper()

def _parseLadderQuest(node):
    try:
        clubs = node.getChildNode('postBattle').getChildNode('clubs')
        return (int(clubs.getChildNode('seasonID').value[0]), int(clubs.getChildNode('division').value[0]), int(clubs.getChildNode('minBattles').value[0]))
    except:
        return None

    return None


class LadderQuest(object):
    __slots__ = ('questID', 'questName', 'questDescr', 'division', 'minBattles', 'questData')

    def __init__(self, questID, questName, questDescr, division, minBattles, questData):
        self.questID = questID
        self.questName = questName
        self.questDescr = questDescr
        self.division = division
        self.minBattles = minBattles
        self.questData = questData


class _QuestsCache(object):

    @classmethod
    def fromDirectory(cls, directory):
        LOG_DEBUG_DEV('clubs_quests initialization')
        questFile = os.path.join(directory, _LADDER_QUESTS_FILE)
        ladderQuests = {}
        for quest in readQuestsFromFile(questFile, EVENT_TYPE.CLUBS_QUEST):
            questID, questName, questDescr, questClientData, node = quest
            ladderQuestData = _parseLadderQuest(node)
            if ladderQuestData is None:
                LOG_DEBUG_DEV('Not all required fields are specified in postBattle/clubs/* for {}.'.format(questID))
                continue
            seasonID, division, minBattles = ladderQuestData
            item = LadderQuest(questID, questName, questDescr, division, minBattles, questClientData)
            ladderQuests.setdefault(seasonID, list()).append(item)

        obj = cls(ladderQuests)
        return obj

    def __init__(self, quests):
        self.__quests = quests
        self.__IDs = self.__getIDsMapping(quests)

    def __getIDsMapping(self, quests):
        result = {}
        for seasonID, seasonQuests in quests.iteritems():
            for quest in seasonQuests:
                result.setdefault(seasonID, set()).add(quest.questID)

        return result

    def __repr__(self):
        res = pformat(self.__quests, depth=3)
        return res

    def getLadderQuestsBySeasonID(self, seasonID):
        return self.__quests.get(seasonID, None)

    def getLadderQuestsIDsBySeasonID(self, seasonID):
        return self.__IDs.get(seasonID, None)


g_cache = None

def init():
    global g_cache
    if g_cache is None:
        g_cache = _QuestsCache.fromDirectory(_CLUBS_QUESTS_DIR)
    return
