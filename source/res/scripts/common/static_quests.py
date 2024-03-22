# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/static_quests.py
import itertools
from collections import namedtuple
import logging
from quest_cache_helpers import readQuestsFromFile
from constants import EVENT_TYPE
from quest_xml_source import collectSections
from ExtensionsManager import g_extensionsManager
STATIC_QUEST_SOURCE_PATH = ['scripts/item_defs/static_quests', '@(EXTENSION)/scripts/item_defs/static_quests']
_logger = logging.getLogger(__name__)

def __isServerOnlyQuest(node):
    info = node.info
    return info.get('serverOnly', False)


StaticQuest = namedtuple('StaticQuest', ['questID', 'questData'])

def __getStaticQuestsFromFileByEventType(sectionList, eventType):
    questsList = (readQuestsFromFile(pathToFile, eventType) for pathToFile in sectionList)
    quests = [ StaticQuest(questID, questClientData) for it in questsList for questID, _, __, questClientData, node in it if it is not None and not __isServerOnlyQuest(node) ]
    _logger.debug('Read %d quests of type %s', len(quests), eventType)
    return quests


def __staticQuestsFromFile(sectionList):
    eventTypes = (EVENT_TYPE.GROUP, EVENT_TYPE.BATTLE_QUEST, EVENT_TYPE.TOKEN_QUEST)
    quests = itertools.chain.from_iterable((__getStaticQuestsFromFileByEventType(sectionList, et) for et in eventTypes))
    return quests


class _StaticQuestsCache(object):

    def __init__(self, quests):
        self.__quests = quests
        _logger.debug('Create all static quests, there size is %d', len(self.__quests))

    def getAllQuests(self):
        return self.__quests

    def getQuestByID(self, questID):
        for quest in self.__quests:
            if quest.questID == questID:
                return quest.questData

        return None


g_staticCache = None

def init():
    global g_staticCache
    if g_staticCache is None:
        staticQuestSectionList = list(itertools.chain.from_iterable((collectSections(ext_path) for path in STATIC_QUEST_SOURCE_PATH for ext_path in g_extensionsManager.getExtensionPath(path))))
        _logger.debug('Length of sources from directory %s with static quests is %d', STATIC_QUEST_SOURCE_PATH[0], len(staticQuestSectionList))
        g_staticCache = _StaticQuestsCache(list(__staticQuestsFromFile(staticQuestSectionList)))
    return
