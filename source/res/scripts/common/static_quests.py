# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/static_quests.py
import itertools
import ResMgr as rmgr
from ExtensionsManager import g_extensionsManager
from quest_cache_helpers import readQuestsFromFile
from quest_xml_source import collectSections
STATIC_QUEST_SOURCE_PATH = ['scripts/item_defs/static_quests']
g_static_quest_cache = None

def staticQuestsFromFile(pathToFiles):
    quests = {}
    for pathToFile in pathToFiles:
        for quest in readQuestsFromFile(pathToFile):
            questID, _, _, questClientData, node = quest
            if not node.info.get('serverOnly', False):
                quests[questID] = questClientData

    return quests


def init():
    global g_static_quest_cache
    if g_static_quest_cache is None:
        extensions = g_extensionsManager.activeExtensions
        availablePaths = STATIC_QUEST_SOURCE_PATH + [ ext.path + path for path in STATIC_QUEST_SOURCE_PATH for ext in extensions if rmgr.isDir(ext.path + path) ]
        staticQuestSectionList = list(itertools.chain.from_iterable((collectSections(path) for path in availablePaths)))
        g_static_quest_cache = staticQuestsFromFile(staticQuestSectionList)
    return
