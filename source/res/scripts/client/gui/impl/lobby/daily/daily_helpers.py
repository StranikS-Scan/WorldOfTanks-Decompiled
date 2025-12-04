# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/daily_helpers.py
import typing
from gui.shared.missions.packers.events import findFirstConditionModel
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from typing import Iterable
    from gui.impl.gen.view_models.common.missions.event_model import EventModel
    from gui.server_events.event_items import Quest, DailyQuest
    from frameworks.wulf.view.array import Array
__all__ = ('needToUpdateQuestsInModel', 'modifyPostbattleConditions', 'isRegularQuestsStateChanged')
NUM_OF_COMMON_DAILY_QUESTS = 3

def areCommonQuestsCompleted(quests):
    numCompletedQuests = len([ q for q in quests if q.isCompleted() ])
    return numCompletedQuests >= NUM_OF_COMMON_DAILY_QUESTS


def needToUpdateQuestsInModel(quests, questsInModel):
    questIds = [ q.getID() for q in quests ]
    return __hasProgressChanged(questIds) or __hasStatusChanged(questIds) or __hasDifferentQuests(questIds, __questModelsIdGen(questsInModel))


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


def modifyPostbattleConditions(quest, questModel):
    postBattleModel = findFirstConditionModel(questModel.postBattleCondition)
    if postBattleModel and postBattleModel.getTotal() == 0:
        battleCount = quest.bonusCond.getConditions().find('battles')
        bonusConditionModel = findFirstConditionModel(questModel.bonusCondition)
        if battleCount and bonusConditionModel:
            postBattleModel.setTotal(bonusConditionModel.getTotal())
            postBattleModel.setCurrent(bonusConditionModel.getCurrent())
            postBattleModel.setEarned(bonusConditionModel.getEarned())
        else:
            postBattleModel.setTotal(1)
            postBattleModel.setCurrent(1 if quest.isCompleted() else 0)


def modifyTokenQuestConditions(quest, questModel):
    token = quest.accountReqs.getConditions().items[0]
    postBattleModel = findFirstConditionModel(questModel.postBattleCondition)
    if postBattleModel:
        postBattleModel.setCurrent(min(token.getNeededCount(), token.getReceivedCount()))
        postBattleModel.setTotal(token.getNeededCount())


def isRegularQuestsStateChanged(state, diff):
    return any((diff[stateVariable] != state for stateVariable in ('enabled', 'regularQuestsEnabled')))
