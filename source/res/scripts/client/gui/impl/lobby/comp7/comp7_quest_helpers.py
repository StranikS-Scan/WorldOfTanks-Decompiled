# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_quest_helpers.py
import logging
import typing
from comp7_common import COMP7_QUEST_PREFIX, COMP7_QUEST_DELIMITER, Comp7QuestType, CLIENT_VISIBLE_QUESTS_TYPE
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from comp7_ranks_common import Comp7Division
    from helpers.server_settings import Comp7PrestigeRanksConfig
_logger = logging.getLogger(__name__)

def isComp7Quest(qID):
    return qID.startswith(COMP7_QUEST_PREFIX) and getComp7QuestType(qID) in CLIENT_VISIBLE_QUESTS_TYPE


def getComp7QuestType(qID):
    qType, _ = __cutComp7Prefix(qID).split(COMP7_QUEST_DELIMITER, 1)
    try:
        qType = Comp7QuestType(qType)
    except ValueError as e:
        _logger.error('Unknown Comp7QuestType for qID=%s: %s', qID, e)
        qType = None

    return qType


def parseComp7RanksQuestID(qID):
    return __getDivisionFromQuest(qID)


def parseComp7TokensQuestID(qID):
    _, __, tokensCount = __cutComp7Prefix(qID).split(COMP7_QUEST_DELIMITER)
    return int(tokensCount)


def parseComp7WeeklyQuestID(qID):
    _, weekQuestID = __cutComp7Prefix(qID).split(COMP7_QUEST_DELIMITER, 1)
    return weekQuestID


def parseComp7PeriodicQuestID(qID):
    return __getDivisionFromQuest(qID)


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getComp7TokensQuests(eventsCache=None):
    quests = eventsCache.getAllQuests(lambda q: isComp7Quest(q.getID()) and getComp7QuestType(q.getID()) == Comp7QuestType.TOKENS)
    quests = {parseComp7TokensQuestID(qID):quest for qID, quest in quests.iteritems()}
    return quests


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getComp7WeeklyQuests(eventsCache=None):
    quests = eventsCache.getAllQuests(lambda q: isComp7Quest(q.getID()) and getComp7QuestType(q.getID()) == Comp7QuestType.WEEKLY and not q.isOutOfDate() and q.isStarted())
    quests = {parseComp7WeeklyQuestID(qID):quest for qID, quest in quests.iteritems()}
    return quests


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def __getDivisionFromQuest(qID, lobbyCtx=None):
    ranksConfig = lobbyCtx.getServerSettings().comp7PrestigeRanksConfig
    _, rankName, divisionName = __cutComp7Prefix(qID).split(COMP7_QUEST_DELIMITER)
    ranksOrder = ranksConfig.ranksOrder
    rankIdx = findFirst(lambda i: ranksOrder[i].lower() == rankName.lower(), range(len(ranksOrder)))
    divisionIdx = int(divisionName) - 1
    division = findFirst(lambda d: d.index == divisionIdx and d.rank == rankIdx, ranksConfig.divisions)
    return division


def __cutComp7Prefix(qID):
    return qID[len(COMP7_QUEST_PREFIX) + 1:]
