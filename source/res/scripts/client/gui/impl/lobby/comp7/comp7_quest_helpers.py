# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_quest_helpers.py
import logging
import re
import typing
from comp7_common import Comp7QuestType, offerWeeklyQuestsRewardTokenBySeasonNumber, offerWeeklyQuestsRewardGiftTokenBySeasonNumber, COMP7_OFFER_YEARLY_REWARD_GIFT_TOKEN_PREFIX, COMP7_OFFER_YEARLY_REWARD_TOKEN_PREFIX, weeklyQuestsCompleteTokenName
from gui.shared.items_cache import ItemsCache
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional, Type
    from comp7_ranks_common import Comp7Division
    from gui.game_control.comp7_controller import Comp7Controller
    from helpers.server_settings import Comp7RanksConfig
_logger = logging.getLogger(__name__)

def isComp7Quest(qID, seasonNumber=None):
    parsedId = Comp7ParsedQuestID(qID)
    return parsedId and (seasonNumber is None or parsedId.season == seasonNumber)


def isComp7VisibleQuest(qID):
    parsedID = Comp7ParsedQuestID(qID)
    return parsedID and parsedID.questType.isVisible()


def getComp7QuestType(qID):
    parsedID = Comp7ParsedQuestID(qID)
    return parsedID.questType if parsedID else None


def isFirstWeeklyQuest(qID):
    qID = Comp7ParsedQuestID(qID)
    return qID and qID.extraInfo == '1_1'


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def parseComp7RanksQuestID(qID, lobbyCtx=None):
    ranksConfig = lobbyCtx.getServerSettings().comp7RanksConfig
    parsedID = Comp7ParsedQuestID(qID)
    divisionID = int(parsedID.extraInfo)
    return findFirst(lambda d: d.dvsnID == divisionID, ranksConfig.divisions)


parseComp7PeriodicQuestID = parseComp7RanksQuestID

def getRequiredTokensCountToComplete(qID):
    return int(Comp7ParsedQuestID(qID).extraInfo)


@dependency.replace_none_kwargs(ctrl=IComp7Controller)
def getComp7WeeklyQuestsCompleteToken(ctrl=None):
    actualSeasonNumber = ctrl.getActualSeasonNumber()
    return weeklyQuestsCompleteTokenName(actualSeasonNumber) if actualSeasonNumber else None


@dependency.replace_none_kwargs(ctrl=IComp7Controller)
def getComp7OfferWeeklyQuestsRewardToken(ctrl=None):
    actualSeasonNumber = ctrl.getActualSeasonNumber()
    return offerWeeklyQuestsRewardTokenBySeasonNumber(actualSeasonNumber) if actualSeasonNumber else None


def isComp7OfferYearlyRewardToken(token):
    return token.startswith(COMP7_OFFER_YEARLY_REWARD_TOKEN_PREFIX)


def isComp7OfferYearlyRewardGiftToken(token):
    return token.startswith(COMP7_OFFER_YEARLY_REWARD_GIFT_TOKEN_PREFIX)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def hasAvailableOfferYearlyRewardGiftTokens(itemsCache=None):
    tokens = itemsCache.items.tokens.getTokens().iteritems()
    return any((amount[1] > 0 and isComp7OfferYearlyRewardGiftToken(name) for name, amount in tokens))


@dependency.replace_none_kwargs(itemsCache=IItemsCache, comp7Controller=IComp7Controller)
def hasAvailableWeeklyQuestsOfferGiftTokens(itemsCache=None, comp7Controller=None):
    season = comp7Controller.getActualSeasonNumber()
    return False if season is None else offerWeeklyQuestsRewardGiftTokenBySeasonNumber(season) in itemsCache.items.tokens.getTokens()


class Comp7ParsedQuestID(object):
    __questIDMatcher = re.compile('comp7_(\\d+)_(\\d+)_({})_(.+)'.format('|'.join((el.value for el in Comp7QuestType)))).match
    __slots__ = ('season', 'questType', 'extraInfo')

    def __new__(cls, questID):
        match = cls.__questIDMatcher(questID)
        if match:
            self = super(cls, cls).__new__(cls)
            mascot, season, questType, self.extraInfo = match.groups()
            self.season = int(season)
            self.questType = Comp7QuestType(questType)
            return self
        else:
            return None
