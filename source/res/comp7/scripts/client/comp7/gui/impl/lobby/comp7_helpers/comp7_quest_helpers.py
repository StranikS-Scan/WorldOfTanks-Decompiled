# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/comp7_helpers/comp7_quest_helpers.py
import logging
import re
import typing
from comp7_common_const import COMP7_OFFER_YEARLY_REWARD_TOKEN_PREFIX, Comp7QuestType, offerWeeklyQuestsRewardTokenPrefixBySeasonNumber, weeklyQuestsCompleteTokenName, COMP7_YEARLY_REWARD_TOKEN, COMP7_OFFER_PREFIX
from gui.server_events.event_items import Quest
from gui.shared.items_cache import ItemsCache
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional, Type, Dict, Tuple, Iterable, Callable
    from comp7_ranks_common import Comp7Division
    from comp7.helpers.comp7_server_settings import Comp7RanksConfig
    from comp7.gui.game_control.comp7_controller import Comp7Controller
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


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def parseComp7RanksQuestID(qID, comp7Controller=None):
    ranksConfig = comp7Controller.getRanksConfig()
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
def getComp7OfferWeeklyQuestsRewardTokenPrefix(ctrl=None):
    actualSeasonNumber = ctrl.getActualSeasonNumber()
    return offerWeeklyQuestsRewardTokenPrefixBySeasonNumber(actualSeasonNumber) if actualSeasonNumber else None


def isComp7OfferYearlyRewardToken(token):
    return token.startswith(COMP7_OFFER_YEARLY_REWARD_TOKEN_PREFIX)


def isComp7OfferYearlyRewardGiftToken(token):
    return isComp7OfferYearlyRewardToken(token) and token.endswith('_gift')


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def hasAvailableOfferYearlyRewardGiftTokens(itemsCache=None):
    tokens = itemsCache.items.tokens.getTokens().iteritems()
    return any((amount[1] > 0 and isComp7OfferYearlyRewardGiftToken(name) for name, amount in tokens))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def hasAvailableOfferTokens(itemsCache=None):
    for name, (_, count) in itemsCache.items.tokens.getTokens().iteritems():
        if name.startswith(COMP7_OFFER_PREFIX) and name.endswith('_gift') and count > 0:
            return True

    return False


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller, itemsCache=IItemsCache)
def getOwnedWeeklyRewardTokens(comp7Controller=None, itemsCache=None):
    season = comp7Controller.getActualSeasonNumber()
    if season is None:
        return {}
    else:
        rewardTokenPrefix = offerWeeklyQuestsRewardTokenPrefixBySeasonNumber(season)
        ownedWeeklyTokens = itemsCache.items.tokens.getTokensByPrefixAndPostfix(prefix=rewardTokenPrefix)
        return ownedWeeklyTokens


def isWeeklyRewardClaimed():
    hasTokenAndNoGiftToken = len(getOwnedWeeklyRewardTokens()) == 1
    return hasTokenAndNoGiftToken


def isWeeklyRewardClaimable():
    hasBothTokenAndGiftToken = len(getOwnedWeeklyRewardTokens()) == 2
    return hasBothTokenAndGiftToken


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def hasYearlyRewardToken(itemsCache=None):
    return itemsCache.items.tokens.getTokenCount(COMP7_YEARLY_REWARD_TOKEN) > 0


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getPeriodicQuestsByDivision(eventsCache=None):
    comp7Quests = eventsCache.getAllQuests(lambda q: isComp7VisibleQuest(q.getID())).values()
    return parseQuestsByDivision(comp7Quests, parseComp7PeriodicQuestID, Comp7QuestType.PERIODIC)


def parseQuestsByDivision(quests, parser, questType):
    questsByDivision = {}
    for quest in quests:
        if getComp7QuestType(quest.getID()) != questType:
            continue
        division = parser(quest.getID())
        if division is not None:
            questsByDivision[division.dvsnID] = quest
        _logger.error('Division number could not be parsed - %s', quest.getID())

    return questsByDivision


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
