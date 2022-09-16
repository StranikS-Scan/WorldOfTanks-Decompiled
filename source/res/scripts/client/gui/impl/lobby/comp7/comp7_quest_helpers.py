# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_quest_helpers.py
import logging
import typing
from comp7_common import COMP7_QUEST_PREFIX, COMP7_QUEST_DELIMITER, Comp7QuestType, CLIENT_VISIBLE_QUESTS_TYPE
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from comp7_ranks_common import Comp7Division
    from helpers.server_settings import Comp7PrestigeRanksConfig
_logger = logging.getLogger(__name__)

def isComp7Quest(qID):
    return qID.startswith(COMP7_QUEST_PREFIX) and getComp7QuestType(qID) in CLIENT_VISIBLE_QUESTS_TYPE


def getComp7QuestType(qID):
    _, qType, __ = qID.split(COMP7_QUEST_DELIMITER, 2)
    try:
        qType = Comp7QuestType(qType)
    except ValueError as e:
        _logger.error('Unknown Comp7QuestType for qID=%s: %s', qID, e)
        qType = None

    return qType


def parseComp7RanksQuestID(qID):
    return __getDivisionFromQuest(qID)


def parseComp7WinsQuestID(qID):
    _, __, winsCount = qID.split(COMP7_QUEST_DELIMITER)
    return int(winsCount)


def parseComp7PeriodicQuestID(qID):
    return __getDivisionFromQuest(qID)


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def __getDivisionFromQuest(qID, lobbyCtx=None):
    ranksConfig = lobbyCtx.getServerSettings().comp7PrestigeRanksConfig
    _, __, rankName, divisionName = qID.split(COMP7_QUEST_DELIMITER)
    ranksOrder = ranksConfig.ranksOrder
    rankIdx = findFirst(lambda i: ranksOrder[i].lower() == rankName.lower(), range(len(ranksOrder)))
    divisionIdx = int(divisionName) - 1
    division = findFirst(lambda d: d.index == divisionIdx and d.rank == rankIdx, ranksConfig.divisions)
    return division
