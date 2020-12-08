# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/celebrity/celebrity_quests_helpers.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_CELEBRITY_QUESTS_VISITED_MASK
from gui.server_events.events_constants import CELEBRITY_MARATHON_PREFIX, CELEBRITY_GROUP_PREFIX
from gui.shared.utils import decorators
from helpers import dependency
from items.components.ny_constants import CelebrityQuestTokenParts, VEH_BRANCH_EXTRA_SLOT_TOKEN
from new_year.ny_processor import SimplifyCelebrityQuestProcessor
from shared_utils import findFirst
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import ICelebritySceneController
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import CelebrityGroup, CelebrityQuest, CelebrityTokenQuest, TokenQuest

@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getCelebrityQuestsGroups(eventsCache=None):
    return eventsCache.getGroups(lambda group: group.isCelebrityQuest())


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getCelebrityQuests(eventsCache=None, filterFunc=None):
    return eventsCache.getCelebrityQuests(filterFunc=filterFunc)


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getCelebrityMarathonQuests(eventsCache=None, filterFunc=None):
    filterFunc = filterFunc or (lambda q: True)
    return eventsCache.getAllQuests(lambda q: q.getID().startswith(CELEBRITY_MARATHON_PREFIX) and filterFunc)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getCelebrityTokens(itemsCache=None):
    tokens = itemsCache.items.tokens.getTokens()
    celebrityTokens = {k:v for k, v in tokens.iteritems() if k.startswith(CELEBRITY_GROUP_PREFIX)}
    return celebrityTokens


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getCelebrityQuestSimplificationCost(quest, level, lobbyContext=None):
    celebrityConfig = lobbyContext.getServerSettings().getNewYearCelebrityConfig()
    return celebrityConfig.calculateSimplificationCost(quest.level, level)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getCelebrityQuestCount(lobbyContext=None):
    celebrityConfig = lobbyContext.getServerSettings().getNewYearCelebrityConfig()
    return celebrityConfig.getQuestCount()


@decorators.process('updating')
def simplifyCelebrityQuest(quest, level):
    yield SimplifyCelebrityQuestProcessor(quest.getID(), level).request()


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


def getQuestCountForExtraSlot():
    for quest in getCelebrityMarathonQuests().itervalues():
        for bonus in quest.getBonuses('tokens', []):
            for tokenRecord in bonus.getTokens().itervalues():
                if tokenRecord.id == VEH_BRANCH_EXTRA_SLOT_TOKEN:
                    return marathonTokenCountExtractor(quest)


@dependency.replace_none_kwargs(celebrityController=ICelebritySceneController)
def isUnseenCelebrityQuestsAvailable(celebrityController=None):
    visitedQuestsMask = AccountSettings.getUIFlag(NY_CELEBRITY_QUESTS_VISITED_MASK)
    visitedQuestsMask |= celebrityController.completedQuestsMask
    for dayNum in (CelebrityQuestTokenParts.getDayNum(qId) for qId in celebrityController.questGroups):
        dayNumMask = 1 << dayNum - 1
        if visitedQuestsMask & dayNumMask == 0:
            return True

    return False


@dependency.replace_none_kwargs(celebrityController=ICelebritySceneController)
def hasCelebrityBubble(celebrityController=None):
    return not celebrityController.isChallengeVisited or isUnseenCelebrityQuestsAvailable()
