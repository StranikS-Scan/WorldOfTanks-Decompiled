# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/missions/missions_helpers.py
import typing
from constants import PREMIUM_TYPE
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.reward_progress.reward_progress_block_model import RewardProgressTypes
from gui.server_events.events_helpers import isEpicQuestEnabled
from gui.shared.formatters import text_styles
from helpers import dependency
from shared_utils import first
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Iterable, Union, AnyStr
    from gui.impl.gen.view_models.common.missions.event_model import EventModel
    from gui.server_events.event_items import Quest, DailyQuest, DailyEpicTokenQuest
    from gui.server_events.conditions import Token
    from frameworks.wulf.view.array import Array
__all__ = ('needToUpdateQuestsInModel',)
NUM_OF_COMMON_DAILY_QUESTS = 3

def areCommonQuestsCompleted(quests):
    numCompletedQuests = len([ q for q in quests if q.isCompleted() ])
    return numCompletedQuests >= NUM_OF_COMMON_DAILY_QUESTS


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isPremiumPlusAccount(itemsCache=None):
    return itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getQuestsToMarkAsViewed(eventsCache=None):
    seenQuests = eventsCache.getDailyQuests().values()
    if isPremiumPlusAccount():
        seenQuests += eventsCache.getPremiumQuests().values()
    return seenQuests


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def markQuestProgressAsViewed(quests=None, eventsCache=None):
    questList = quests if quests else getQuestsToMarkAsViewed()
    for seenQuest in questList:
        eventsCache.questsProgress.markQuestProgressAsViewed(seenQuest.getID())


def needToUpdateQuestsInModel(quests, questsInModel):
    questIds = [ q.getID() for q in quests ]
    return __hasProgressChanged(questIds) or __hasStatusChanged(questIds) or __hasDifferentQuests(questIds, __questModelsIdGen(questsInModel))


def needToUpdateQuestsInModelByIds(quests, questIdsInModel):
    questIds = [ q.getID() for q in quests ]
    return __hasProgressChanged(questIds) or __hasStatusChanged(questIds) or __hasDifferentQuests(questIds, questIdsInModel)


def getDailyEpicQuestToken(quest):
    return first((token for token in quest.accountReqs.getTokens() if token.isDailyQuest()))


def formatCompleteCount(completedQuestsCount, totalCount, isIncreased=False):
    if completedQuestsCount == totalCount:
        styleFormatter = text_styles.statsIncrease if isIncreased else text_styles.bonusAppliedText
    else:
        styleFormatter = text_styles.highlightText if isIncreased else text_styles.stats
    return styleFormatter(completedQuestsCount)


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getRewardProgressType(winBackData=None, eventsCache=None):
    if winBackData:
        return RewardProgressTypes.WINBACK
    else:
        return RewardProgressTypes.EPICQUEST if isEpicQuestEnabled() and eventsCache.getDailyEpicQuest() is not None else RewardProgressTypes.DISABLED


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def __hasProgressChanged(ids, eventsCache=None):
    hasProgressedFunc = eventsCache.questsProgress.hasQuestProgressed
    return any((hasProgressedFunc(index) for index in ids))


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def __hasStatusChanged(ids, eventsCache=None):
    for index in ids:
        if eventsCache.questsProgress.getQuestCompletionChanged(index):
            return True

    return False


def __hasDifferentQuests(questIds, viewModelIds):
    return sorted(questIds) != sorted(viewModelIds)


def __questModelsIdGen(dailyQuests):
    for dailyQuest in dailyQuests:
        yield dailyQuest.getId()
