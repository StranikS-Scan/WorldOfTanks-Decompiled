# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/lobby/views/quests_helper.py
import typing
from grinch_progression.gui.impl.gen.view_models.views.lobby.views.enums import VehicleRole
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional, Tuple, List
    from gui.server_events.event_items import Quest

class VehicleRoleStr(object):
    CARRIER = 'carrier'
    SUPPORT = 'support'
    ASSAULT = 'assault'
    ALL = (CARRIER, SUPPORT, ASSAULT)


def vehicleRoleStrToModel(roleStr):
    return VehicleRole(roleStr)


class Complexity(object):
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'
    ALL = (EASY, MEDIUM, HARD)


SEPARATOR = ':'
PREFIX = 'grinch'
SPECIAL_ADD_PREFIX = 'progression'
CHAPTER = 'chapter'

def _splitQuestID(questID, partsCount=3):
    if not isinstance(questID, basestring):
        return None
    else:
        parts = tuple(str(questID).split(SEPARATOR))
        return None if len(parts) != partsCount or parts[0] != PREFIX else parts


def isGrinchWeekendQuestID(questID, neededRole=None):
    parts = _splitQuestID(questID)
    if not parts:
        return False
    else:
        questPrefix, role, chapterNum = parts
        return questPrefix == PREFIX and (role in VehicleRoleStr.ALL if neededRole is None else role == neededRole) and chapterNum.startswith(CHAPTER)


def isSpecialQuestQuest(questID):
    parts = _splitQuestID(questID, 4)
    if not parts:
        return False
    questPrefix, specialPrefix, questComplexity, questID = parts
    return questPrefix == PREFIX and specialPrefix == SPECIAL_ADD_PREFIX and questComplexity in Complexity.ALL and questID.startswith('quest')


def isDailyModifiersQuest(questID):
    return questID.startswith('grinch:modifiers')


def makeSpecialQuestIDFromToken(token):
    parts = _splitQuestID(token)
    if parts is None:
        return
    else:
        _, questComplexity, questID = parts
        return SEPARATOR.join((PREFIX,
         SPECIAL_ADD_PREFIX,
         questComplexity,
         questID))


def isSpecialDailyToken(token):
    parts = _splitQuestID(token)
    if not parts:
        return False
    questPrefix, complexity, questID = parts
    return questPrefix == PREFIX and complexity in Complexity.ALL and questID.startswith('quest')


def isGrinchRandom(token):
    parts = _splitQuestID(token)
    if not parts:
        return False
    questPrefix, randomQuests, complexity = parts
    return questPrefix == PREFIX and complexity in Complexity.ALL and randomQuests.startswith('random')


def getRoleStr(quest):
    parts = _splitQuestID(quest.getID())
    return '' if not parts else parts[1]


def getChupterNum(quest):
    parts = _splitQuestID(quest.getID())
    if not parts:
        return -1
    chapter, number = parts[-1].split('_')
    return int(number) if chapter == CHAPTER and number.isdigit() else 0


def sortWeekendQuestKey(quest):
    return getChupterNum(quest)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def iterSpecialQuestsTokens(filterFunc=None, itemsCache=None):
    return (token for token in itemsCache.items.tokens.getTokens().iterkeys() if isSpecialDailyToken(token) and (filterFunc is None or filterFunc(token)))


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getSpecialQuestQuestByToken(token, eventsCache=None):
    return eventsCache.getQuestByID(makeSpecialQuestIDFromToken(token))


def getSpecialQuestQuests():
    result = []
    for token in iterSpecialQuestsTokens():
        quest = getSpecialQuestQuestByToken(token)
        if quest:
            result.append(quest)

    return result


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getWeekendQuests(role=VehicleRoleStr.CARRIER, eventsCache=None):
    result = eventsCache.getAllQuests(lambda q: isGrinchWeekendQuestID(q.getID(), role)).values()
    return sorted(result, key=sortWeekendQuestKey)


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getDailyModifiersQuest(eventsCache=None):
    return eventsCache.getAllQuests(lambda q: isDailyModifiersQuest(q.getID())).values()


def isGrinchQuest(qID):
    return isGrinchWeekendQuestID(qID) or isSpecialQuestQuest(qID)
