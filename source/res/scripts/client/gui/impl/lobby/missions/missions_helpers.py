# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/missions/missions_helpers.py
import typing
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from typing import Iterable
    from gui.impl.gen.view_models.common.missions.event_model import EventModel
    from gui.server_events.event_items import Quest
__all__ = ('needToUpdateQuestsInModel',)

def needToUpdateQuestsInModel(quests, questsInModel):
    return __hasProgressChanged(__questsIdGen(quests)) or __hasStatusChanged(__questsIdGen(quests)) or __hasNewQuest(__questsIdGen(quests), __questModelsIdGen(questsInModel))


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


def __hasNewQuest(questIds, viewModelIds):
    for index in questIds:
        if index not in viewModelIds:
            return True

    return False


def __questsIdGen(dailyQuests):
    for dailyQuest in dailyQuests:
        yield dailyQuest.getID()


def __questModelsIdGen(dailyQuests):
    for dailyQuest in dailyQuests:
        yield dailyQuest.getId()
