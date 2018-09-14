# Embedded file name: scripts/common/clubs_quests.py
from collections import namedtuple
import os
from pprint import pformat
import time
from constants import ITEM_DEFS_PATH, EVENT_TYPE, IS_CLIENT
from debug_utils import LOG_SVAN_DEV, LOG_WARNING
import quest_xml_source
if IS_CLIENT:
    from helpers import i18n
else:
    from web_stubs import i18n
_CLUBS_QUESTS_DIR = ITEM_DEFS_PATH + 'clubs_quests/'
_LADDER_QUESTS_FILE = 'ladder_quests.xml'
_ERROR_TEMPLATE = 'Error happened during parsing ClubsQuests. file: {} details: {} extras: {}'

class QuestsParsingError(RuntimeError):

    def __init__(self, filePath, msg, **kwargs):
        self.filePath = filePath
        self.extras = kwargs
        msg = _ERROR_TEMPLATE.format(filePath, msg, kwargs)
        RuntimeError.__init__(self, msg)


def parseLadderQuest(node):
    seasonID = None
    division = None
    minBattles = None
    try:
        clubs = node.getChildNode('postBattle').getChildNode('clubs')
        seasonID = int(clubs.getChildNode('seasonID').value[0])
        division = int(clubs.getChildNode('division').value[0])
        minBattles = int(clubs.getChildNode('minBattles').value[0])
    except:
        pass

    return (seasonID, division, minBattles)


LadderQuest = namedtuple('LadderQuest', ('questID', 'questName', 'questDescr', 'division', 'minBattles', 'questData'))

class _QuestsCache(object):

    @classmethod
    def fromDirectory(cls, directory):
        LOG_SVAN_DEV('clubs_quests initialization')
        curTime = int(time.time())
        xmlSource = quest_xml_source.Source()
        questFile = os.path.join(directory, _LADDER_QUESTS_FILE)
        nodes = xmlSource.readFromInternalFile(questFile, curTime)
        nodes = nodes.get(EVENT_TYPE.CLUBS_QUEST, None)
        ladderQuests = {}
        if nodes is None:
            LOG_WARNING(questFile, 'Event type EVENT_TYPE.CLUBS_QUEST not found.')
        else:
            for node in nodes:
                info = node.info
                questID = info.get('id', None)
                if not questID:
                    raise QuestsParsingError(questFile, 'Unique quest id not found.')
                if questID in ladderQuests:
                    raise QuestsParsingError(questFile, 'Duplicate questID detected.', questID=questID)
                seasonID, division, minBattles = parseLadderQuest(node)
                questData = info.get('questClientData', None)
                if seasonID is None or division is None or questData is None:
                    LOG_SVAN_DEV('Not all required fields are specified in postBattle/clubs/* for {}.'.format(questID))
                    continue
                questName = questData.get('name', None)
                if questName:
                    questName = i18n.makeString(questName['key'])
                questDescr = questData.get('description', None)
                if questDescr:
                    questDescr = i18n.makeString(questDescr['key'])
                item = LadderQuest(questID, questName, questDescr, division, minBattles, questData)
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
