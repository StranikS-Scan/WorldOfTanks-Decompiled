# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/common/armory_quests_common/armory_quests_cache.py
from ExtensionsManager import g_extensionsManager
from armory_yard_constants import FEATURE_NAME_BASE
from constants import ITEM_DEFS_PATH
from quest_cache_helpers import readQuestsFromFile
from quest_xml_source import collectSections
QUEST_SOURCE_PATH = ITEM_DEFS_PATH + 'armory_quests'
g_armory_quests_cache = None

def armoryQuestsFromFile(pathToFiles):
    quests = {}
    for pathToFile in pathToFiles:
        for quest in readQuestsFromFile(pathToFile):
            questID, _, _, questClientData, node = quest
            if not node.info.get('serverOnly', False):
                reqToken = node.info.get('requiredToken', '')
                personalQuests = quests.setdefault(reqToken, {})
                personalQuests[questID] = questClientData

    return quests


def init(force=False):
    global g_armory_quests_cache
    if g_armory_quests_cache is None or force:
        g_armory_quests_cache = armoryQuestsFromFile(getArmoryQuestsSectionList())
    return


def getArmoryQuestsCache():
    init(force=False)
    return g_armory_quests_cache


def getArmoryQuestsSectionList():
    armoryExt = g_extensionsManager.getActiveExtensionByName(FEATURE_NAME_BASE)
    return collectSections(armoryExt.path + QUEST_SOURCE_PATH) if armoryExt else []
