# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_quest_helpers.py
import logging
import re
from enum import Enum
import typing
from comp7_common import Comp7QuestType, CLIENT_VISIBLE_QUESTS_TYPE, COMP7_QUEST_ID_REGEXP, weeklyRewardTokenBySeasonNumber
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from comp7_ranks_common import Comp7Division
    from helpers.server_settings import Comp7RanksConfig
_logger = logging.getLogger(__name__)

def isComp7Quest(qID, seasonNumber=None):
    parsedId = _QuestIDParser(qID)
    return parsedId.isComp7Quest() and (seasonNumber is None or parsedId.season == seasonNumber)


def isComp7VisibleQuest(qID):
    parsedID = _QuestIDParser(qID)
    return parsedID.isComp7Quest() and parsedID.questType in CLIENT_VISIBLE_QUESTS_TYPE


def getComp7QuestType(qID):
    return _QuestIDParser(qID).questType


def parseComp7RanksQuestID(qID):
    return __getDivisionFromQuest(qID)


def getRequiredTokensCountToComplete(qID):
    return int(_QuestIDParser(qID).extraInfo)


def parseComp7WeeklyQuestID(qID):
    return _QuestIDParser(qID).extraInfo


def parseComp7PeriodicQuestID(qID):
    return __getDivisionFromQuest(qID)


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getComp7WeeklyProgressionQuests(eventsCache=None):
    quests = eventsCache.getAllQuests(lambda q: isComp7VisibleQuest(q.getID()) and getComp7QuestType(q.getID()) == Comp7QuestType.TOKENS)
    quests = {getRequiredTokensCountToComplete(qID):quest for qID, quest in quests.iteritems()}
    return quests


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getComp7WeeklyQuests(eventsCache=None):
    quests = eventsCache.getAllQuests(lambda q: isComp7VisibleQuest(q.getID()) and getComp7QuestType(q.getID()) == Comp7QuestType.WEEKLY and not q.isOutOfDate() and q.isStarted())
    quests = {parseComp7WeeklyQuestID(qID):quest for qID, quest in quests.iteritems()}
    return quests


@dependency.replace_none_kwargs(ctrl=IComp7Controller)
def getActualSeasonWeeklyRewardToken(ctrl=None):
    actualSeasonNumber = ctrl.getActualSeasonNumber()
    return weeklyRewardTokenBySeasonNumber(actualSeasonNumber) if actualSeasonNumber else None


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def __getDivisionFromQuest(qID, lobbyCtx=None):
    parsedID = _QuestIDParser(qID)
    ranksConfig = lobbyCtx.getServerSettings().comp7RanksConfig
    divisionID = int(parsedID.extraInfo)
    return findFirst(lambda d: d.dvsnID == divisionID, ranksConfig.divisions)


class _QuestIDParser(object):

    class _GroupIDs(Enum):
        MASKOT = 0
        SEASON = 1
        TYPE = 2
        EXTRA_INFO = 3

    __ID_REGEXP = re.compile(COMP7_QUEST_ID_REGEXP)

    def __init__(self, questID):
        self.__match = self.__ID_REGEXP.match(questID)
        self.__groups = self.__match.groups() if self.__match else None
        return

    def isComp7Quest(self):
        return self.__match is not None

    @property
    def questType(self):
        rawQuestType = self.__getGroupValue(self._GroupIDs.TYPE)
        return Comp7QuestType(rawQuestType) if rawQuestType else None

    @property
    def season(self):
        return int(self.__getGroupValue(self._GroupIDs.SEASON))

    @property
    def extraInfo(self):
        return self.__getGroupValue(self._GroupIDs.EXTRA_INFO)

    def __getGroupValue(self, groupID):
        return self.__groups[groupID.value] if self.__match else None
