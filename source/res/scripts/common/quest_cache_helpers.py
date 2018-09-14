# Embedded file name: scripts/common/quest_cache_helpers.py
import time
from constants import EVENT_TYPE, IS_CLIENT
from debug_utils import LOG_WARNING
import quest_xml_source
if IS_CLIENT:
    from helpers import i18n
else:
    from web_stubs import i18n

def makeI18nString(string):
    return i18n.makeString(string)


def _getEventName(eventType):
    return EVENT_TYPE.TYPE_TO_NAME.get(eventType, '<wrong EVENT_TYPE>')


def readQuestsFromFile(filePath, eventType):
    xmlSource = quest_xml_source.Source()
    nodes = xmlSource.readFromInternalFile(filePath, int(time.time()))
    nodes = nodes.get(eventType, None)
    questIDs = set()
    if nodes is None:
        LOG_WARNING(filePath, 'No quests of type {} were found in {}.'.format(_getEventName(eventType), filePath))
        return
    else:
        for node in nodes:
            info = node.info
            questID = info.get('id', None)
            if not questID:
                raise Exception('questID is not set for a quest in {}, eventType: {}'.format(filePath, _getEventName(eventType)))
            if questID in questIDs:
                raise Exception('duplicate questID: {} in {}, eventType: {}'.format(questID, filePath, _getEventName(eventType)))
            questIDs.add(questID)
            questData = info.get('questClientData', None)
            if questData is None:
                LOG_WARNING(filePath, '"questClientData" not set for {} in {}'.format(questID, filePath))
                continue
            questName = questData.get('name', None)
            if questName:
                questName = makeI18nString(questName['key'])
            questDescr = questData.get('description', None)
            if questDescr:
                questDescr = makeI18nString(questDescr['key'])
            yield (questID,
             questName,
             questDescr,
             questData,
             node)

        return
