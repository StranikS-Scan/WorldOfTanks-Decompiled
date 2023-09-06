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
    from helpers.server_settings import Comp7RanksConfig
_logger = logging.getLogger(__name__)

def isComp7Quest(qID):
    return qID.startswith(COMP7_QUEST_PREFIX)


def isComp7VisibleQuest(qID):
    return isComp7Quest(qID) and getComp7QuestType(qID) in CLIENT_VISIBLE_QUESTS_TYPE


def getComp7QuestType(qID):
    qType, _, __ = __cutComp7Prefix(qID).partition(COMP7_QUEST_DELIMITER)
    return findFirst(lambda t: t.value == qType, Comp7QuestType)


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
    quests = eventsCache.getAllQuests(lambda q: isComp7VisibleQuest(q.getID()) and getComp7QuestType(q.getID()) == Comp7QuestType.TOKENS)
    quests = {parseComp7TokensQuestID(qID):quest for qID, quest in quests.iteritems()}
    return quests


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getComp7WeeklyQuests(eventsCache=None):
    quests = eventsCache.getAllQuests(lambda q: isComp7VisibleQuest(q.getID()) and getComp7QuestType(q.getID()) == Comp7QuestType.WEEKLY and not q.isOutOfDate() and q.isStarted())
    quests = {parseComp7WeeklyQuestID(qID):quest for qID, quest in quests.iteritems()}
    return quests


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def __getDivisionFromQuest(qID, lobbyCtx=None):
    ranksConfig = lobbyCtx.getServerSettings().comp7RanksConfig
    divisionID = int(qID.split(COMP7_QUEST_DELIMITER)[-1])
    return findFirst(lambda d: d.dvsnID == divisionID, ranksConfig.divisions)


def __cutComp7Prefix(qID):
    return qID[len(COMP7_QUEST_PREFIX) + 1:]
