# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/celebrity/celebrity_quests_helpers.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_CELEBRITY_ADD_QUESTS_VISITED_MASK, NY_CELEBRITY_DAY_QUESTS_VISITED_MASK, NY_DOG_PAGE_VISITED, NY_CAT_PAGE_VISITED
from gui.server_events.events_constants import CELEBRITY_MARATHON_PREFIX, CELEBRITY_QUESTS_PREFIX
from helpers import dependency
from items.components.ny_constants import CelebrityQuestTokenParts, NyCurrency
from new_year.ny_constants import GuestQuestTokenActionType, GuestsQuestsTokens
from ny_common.settings import GuestsQuestsConsts
from shared_utils import findFirst, first
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import ICelebritySceneController, INewYearController
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, Iterable, List, Optional, Union
    from gui.server_events.bonuses import SimpleBonus
    from gui.shared.utils.requesters import TokensRequester
    from gui.server_events.event_items import CelebrityQuest, CelebrityTokenQuest, TokenQuest, Quest
    from ny_common.GuestsQuestsConfig import GuestsQuestsConfig, GuestQuests, GuestQuest

def getCelebrityQuests():
    result = {}
    for token in iterCelebrityActiveQuestsIDs():
        quest = getCelebrityQuestByFullID(token)
        if quest:
            result[quest.getID()] = quest

    return result


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def iterCelebrityActiveQuestsIDs(filterFunc=None, itemsCache=None):
    return (token for token in itemsCache.items.tokens.getTokens().iterkeys() if CelebrityQuestTokenParts.isCelebrityFullQuestID(token) and (filterFunc is None or filterFunc(token)))


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getCelebrityQuestBonusesByFullQuestID(token, eventsCache=None):
    quest = getCelebrityQuestByFullID(token) if CelebrityQuestTokenParts.isDayQuestID(token) else (getCelebrityTokenQuestByFullQuestID(token) if CelebrityQuestTokenParts.isAddQuestID(token) else (eventsCache.getQuestByID(token) if CelebrityQuestTokenParts.isFinalAdditionalQuestID(token) else None))
    return quest.getBonuses() if quest is not None else []


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getCelebrityQuestByFullID(token, eventsCache=None):
    return eventsCache.getQuestByID(CelebrityQuestTokenParts.makeQuestIDFromFullQuestID(token))


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getCelebrityTokenQuestByFullQuestID(token, eventsCache=None):
    return eventsCache.getQuestByID(CelebrityQuestTokenParts.makeTokenQuestIDFromFullQuestID(token))


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getCelebrityMarathonQuests(filterFunc=None, eventsCache=None):
    filterFunc = filterFunc or (lambda q: True)
    return eventsCache.getAllQuests(lambda q: q.getID().startswith(CELEBRITY_MARATHON_PREFIX) and filterFunc)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getCelebrityTokens(itemsCache=None):
    tokens = itemsCache.items.tokens.getTokens()
    celebrityTokens = {k:v for k, v in tokens.iteritems() if k.startswith(CELEBRITY_QUESTS_PREFIX)}
    return celebrityTokens


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getRerollsCount(itemsCache=None):
    token = itemsCache.items.tokens.getToken(CelebrityQuestTokenParts.REROLL_TOKEN)
    if token:
        _, count = token
        return max(count, 0)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getCelebrityQuestSimplificationCost(quest, level, lobbyContext=None):
    celebrityConfig = lobbyContext.getServerSettings().getNewYearCelebrityConfig()
    return celebrityConfig.calculateSimplificationCost(quest.level, level)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getCelebrityQuestCount(lobbyContext=None):
    celebrityConfig = lobbyContext.getServerSettings().getNewYearCelebrityConfig()
    return celebrityConfig.getQuestCount()


@dependency.replace_none_kwargs(celebrityController=ICelebritySceneController)
def getFinalCelebrityMarathonQuest(celebrityController=None):
    return max((quest for quest in celebrityController.marathonQuests.itervalues()), key=marathonTokenCountExtractor)


def marathonTokenCountExtractor(quest):
    tokenCondition = findFirst(lambda t: t.getID() == CELEBRITY_MARATHON_PREFIX, quest.accountReqs.getTokens())
    return 0 if tokenCondition is None else tokenCondition.getNeededCount()


def marathonQuestsFilter(quests):
    for questName in quests:
        if questName.startswith(CELEBRITY_MARATHON_PREFIX):
            yield questName


def finalAdditionalQuestsFilter(quests):
    for questID in quests:
        if CelebrityQuestTokenParts.isFinalAdditionalQuestID(questID):
            yield questID


def isDogPageVisited():
    return AccountSettings.getUIFlag(NY_DOG_PAGE_VISITED)


def isCatPageVisited():
    return AccountSettings.getUIFlag(NY_CAT_PAGE_VISITED)


@dependency.replace_none_kwargs(celebrityController=ICelebritySceneController)
def isUnseenCelebrityQuestsAvailable(celebrityController=None):
    visitedDayQuestsMask = AccountSettings.getUIFlag(NY_CELEBRITY_DAY_QUESTS_VISITED_MASK)
    visitedAddQuestsMask = AccountSettings.getUIFlag(NY_CELEBRITY_ADD_QUESTS_VISITED_MASK)
    visitedDayQuestsMask |= celebrityController.completedDayQuestsMask
    visitedAddQuestsMask |= celebrityController.completedAddQuestsMask
    for token in iterCelebrityActiveQuestsIDs():
        qType, qNum = CelebrityQuestTokenParts.getFullQuestOrderInfo(token)
        qNumMask = 1 << qNum - 1
        anyUnseen = qType == CelebrityQuestTokenParts.DAY and visitedDayQuestsMask & qNumMask == 0 or qType == CelebrityQuestTokenParts.ADD and visitedAddQuestsMask & qNumMask == 0
        if anyUnseen:
            return True

    return False


@dependency.replace_none_kwargs(celebrityController=ICelebritySceneController, nyController=INewYearController)
def hasCelebrityBubble(celebrityController=None, nyController=None):
    isTokenDogAvailable = nyController.isDogTokenReceived()
    isDogVisited = isDogPageVisited() if isTokenDogAvailable else True
    sacksCount = nyController.sacksHelper.getSacksCount()
    isTokenCatAvailable = nyController.isCatTokenReceived()
    isCatVisited = isCatPageVisited() if isTokenCatAvailable else True
    return not celebrityController.isChallengeVisited or isUnseenCelebrityQuestsAvailable() or not isDogVisited or not isCatVisited or sacksCount > 0


@dependency.replace_none_kwargs(nyController=INewYearController)
def getDogLevel(nyController=None):
    token = GuestsQuestsTokens.TOKEN_DOG
    return nyController.getTokenCount(token) - 1 if nyController.isTokenReceived(token) else -1


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _guestsQuestsAvailableDependenciesChecker(dependencies, itemsCache=None):
    tokens = itemsCache.items.tokens
    for dependencyType, dependencyData in dependencies.iteritems():
        if dependencyType == GuestsQuestsConsts.TOKEN:
            for tokenID, tokenCount in dependencyData.iteritems():
                if tokens.getTokenCount(tokenID) != tokenCount:
                    return False

    return True


def _getGuestRewardsActionTypeChecker(guestName, tokenType):
    tokenMask = 'ny:{}:{}'.format(guestName, tokenType)
    return lambda t: t.startswith(tokenMask)


class GuestsQuestsConfigHelper(object):
    __slots__ = ()

    @staticmethod
    @dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
    def getNYGuestsQuestsConfig(lobbyCtx=None):
        return lobbyCtx.getServerSettings().getNewYearGuestsQuestsConfig()

    @classmethod
    def getQuestsIDs(cls):
        config = cls.getNYGuestsQuestsConfig()
        questsIDs = []
        for guestName in GuestsQuestsTokens.GUESTS_ALL:
            questsIDs.extend([ quest.getQuestID() for quest in config.getQuestsByGuest(guestName).getQuests() ])

        return questsIDs

    @classmethod
    def hasQuestID(cls, questID):
        return questID in cls.getQuestsIDs()

    @classmethod
    def getNYQuestsByGuest(cls, guestName):
        config = cls.getNYGuestsQuestsConfig()
        return config.getQuestsByGuest(guestName)

    @classmethod
    def getAnimatedGuestQuests(cls, guestName):
        return cls._getGuestsActionQuests(guestName, GuestQuestTokenActionType.ANIM)

    @classmethod
    def getStoryGuestQuests(cls, guestName):
        return cls._getGuestsActionQuests(guestName, GuestQuestTokenActionType.STORY)

    @classmethod
    def getDecorationGuestQuests(cls, guestName):
        return cls._getGuestsActionQuests(guestName, GuestQuestTokenActionType.DECORATION)

    @classmethod
    def getGuestQuestByQuestID(cls, questID):
        for guestName in GuestsQuestsTokens.GUESTS_ALL:
            questsHolder = cls.getNYQuestsByGuest(guestName)
            quest = questsHolder.getQuestByQuestID(questID)
            if quest:
                return quest

        return None

    @classmethod
    def getGuestsActionTokens(cls, guestName, tokenType=''):
        config = cls.getNYGuestsQuestsConfig()
        quests = config.getQuestsByGuest(guestName)
        if quests:
            checker = _getGuestRewardsActionTypeChecker(guestName, tokenType)
            tokenRewards = []
            for quest in quests.getQuests():
                tokenRewards.extend(quest.getQuestTokensRewards(checker).keys())

            return tokenRewards
        return []

    @classmethod
    def getQuestActionToken(cls, quest, tokenType=''):
        if quest is None:
            return
        else:
            guestName = cls.getGuestNameByQuest(quest)
            checker = _getGuestRewardsActionTypeChecker(guestName, tokenType)
            tokens = quest.getQuestTokensRewards(checker)
            return first(tokens.keys())

    @classmethod
    def getQuestPrice(cls, guestQuest):
        price = guestQuest.getQuestPrice()
        currency = findFirst(None, price, NyCurrency.CRYSTAL)
        return (currency, price.get(currency, 0))

    @classmethod
    def getQuestIndex(cls, guestQuest):
        searchID = guestQuest.getQuestID()
        guestName = cls.getGuestNameByQuest(guestQuest)
        questsHolder = cls.getNYQuestsByGuest(guestName)
        for idx, quest in enumerate(questsHolder.getQuests()):
            if quest.getQuestID() == searchID:
                return idx

    @classmethod
    def isQuestAvailable(cls, guestQuest):
        return guestQuest.isQuestAvailable(_guestsQuestsAvailableDependenciesChecker)

    @classmethod
    def getGuestNameByQuest(cls, quest):
        quetsID = quest.getQuestID()
        for guestName in GuestsQuestsTokens.GUESTS_ALL:
            quests = cls.getNYQuestsByGuest(guestName)
            if quests is None:
                continue
            if quests.getQuestByQuestID(quetsID) is not None:
                return guestName

        return

    @classmethod
    def hasAnyAvailableGuestQuest(cls, guestName):
        guestQuests = cls.getNYQuestsByGuest(guestName)
        if guestQuests is None:
            return False
        else:
            for quest in guestQuests.getQuests():
                if cls.isQuestAvailable(quest):
                    return True

            return False

    @classmethod
    def getQuestsWithRewards(cls, tokenIDs):
        quests = set()
        for guestName in GuestsQuestsTokens.GUESTS_ALL:
            questsHolder = cls.getNYQuestsByGuest(guestName)
            for quest in questsHolder.getQuests():
                if any([ tID for tID in tokenIDs if tID in quest.getQuestTokensRewards().keys() ]):
                    quests.add(quest)

        return quests

    @classmethod
    def _getGuestsActionQuests(cls, guestName, tokenType=''):
        quests = cls.getNYQuestsByGuest(guestName)
        if quests:
            checker = _getGuestRewardsActionTypeChecker(guestName, tokenType)
            actionQuests = [ quest for quest in quests.getQuests() if any(quest.getQuestTokensRewards(checker)) ]
            return actionQuests
        return []

    @classmethod
    def _getTokensRewardCount(cls, tokenID):
        count = 0
        checker = lambda tID: tID == tokenID
        for guestName in GuestsQuestsTokens.GUESTS_ALL:
            questsHolder = cls.getNYQuestsByGuest(guestName)
            for quest in questsHolder.getQuests():
                tokens = quest.getQuestTokensRewards(checker)
                count += sum((v.get('count', 0) for v in tokens.values()))

        return count
