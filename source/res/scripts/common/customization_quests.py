# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/customization_quests.py
import itertools
from collections import namedtuple
import persistent_data_cache_common as pdc
from quest_cache_helpers import readQuestsFromFile
from quest_xml_source import collectSections, QuestValidationSerializer
from constants import EVENT_TYPE
C11N_QUESTS_PROGRESSION_SOURCE_PATH = ['scripts/item_defs/customization/progression/quests']
CustomizationQuest = namedtuple('CustomizationQuest', ('questID', 'questName', 'questDescr', 'questClientData'))
g_cust_cache = None

def customizationQuestsFromFile(pathToFiles, auxData=None):
    quests = {}
    for pathToFile in pathToFiles:
        for et in EVENT_TYPE.QUEST_USE_FOR_C11N_PROGRESS:
            for quest in readQuestsFromFile(pathToFile, et, auxData):
                questID, questName, questDescr, questClientData, _ = quest
                quests[questID] = CustomizationQuest(questID, questName, questDescr, questClientData)

    return quests


def _createCache():
    customizationQuestSectionList = list(itertools.chain.from_iterable((collectSections(path) for path in C11N_QUESTS_PROGRESSION_SOURCE_PATH)))
    auxData = {}
    return (customizationQuestsFromFile(customizationQuestSectionList, auxData), auxData)


def init():
    global g_cust_cache
    if g_cust_cache is None:
        g_cust_cache, _ = pdc.load('customization_quests_cache', _createCache, QuestValidationSerializer())
    return
