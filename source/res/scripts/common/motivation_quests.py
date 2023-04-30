# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/motivation_quests.py
import os
from pprint import pformat
from quest_cache_helpers import readQuestsFromFile, makeI18nString
from constants import ITEM_DEFS_PATH, EVENT_TYPE
from debug_utils import LOG_WARNING
_QUESTS_DIR = os.path.join(ITEM_DEFS_PATH, 'motivation_quests/')
_QUESTS_FILE = 'quests.xml'

def __parseMotivationsQuest(node):
    try:
        info = node.info
        return (makeI18nString(info['advice']['key']), makeI18nString(info['requirements']['key']), makeI18nString(info['congratulation']['key']))
    except:
        return None

    return None


class MotivationQuest(object):
    __slots__ = ('questID', 'questName', 'questDescr', 'advice', 'requirements', 'congratulation', 'questData')

    def __init__(self, questID, questName, questDescr, advice, requirements, congratulation, questData):
        self.questID = questID
        self.questName = questName
        self.questDescr = questDescr
        self.advice = advice
        self.requirements = requirements
        self.congratulation = congratulation
        self.questData = questData


def motivationQuestsFromFile(pathToFile):
    quests = {}
    for quest in readQuestsFromFile(pathToFile, EVENT_TYPE.MOTIVE_QUEST):
        questID, questName, questDescr, questClientData, node = quest
        questData = __parseMotivationsQuest(node)
        if questData is None:
            LOG_WARNING('Not all required fields are specified in quest for {}.'.format(questID))
            continue
        advice, requirements, congratulation = questData
        quests[questID] = MotivationQuest(questID, questName, questDescr, advice, requirements, congratulation, questClientData)

    return quests


class _QuestsCache(object):

    def __init__(self, quests):
        self.__quests = quests

    def __contains__(self, questID):
        return questID in self.__quests

    def getAllQuests(self):
        return self.__quests.values()

    def getQuestIDs(self):
        return self.__quests.keys()

    def getQuestByID(self, questID):
        return self.__quests[questID]

    def __repr__(self):
        res = pformat(self.__quests, depth=3)
        return res


g_cache = None

def init():
    global g_cache
    if g_cache is None:
        questFilePath = os.path.join(_QUESTS_DIR, _QUESTS_FILE)
        g_cache = _QuestsCache(motivationQuestsFromFile(questFilePath))
    return
