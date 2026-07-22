# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/quests_progress_visitor.py
import typing
import Event
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from typing import List
    from gui.impl.gen.view_models.common.missions.quest_model import QuestModel
    from gui.server_events.event_items import Quest
    from frameworks.wulf import Array

class QuestsProgressVisitor(object):
    __slots__ = ('__questsToMark', '__visitedGroups', 'onGroupsVisited')
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        self.__questsToMark = {}
        self.__visitedGroups = set()
        self.onGroupsVisited = Event.Event()

    def reuse(self):
        self.__questsToMark.clear()
        self.__visitedGroups.clear()

    def clear(self):
        self.onGroupsVisited.clear()
        self.__questsToMark.clear()
        self.__visitedGroups.clear()

    def getWaitVisitGroups(self):
        return self.__questsToMark.keys()

    def isGroupVisited(self, groupId):
        return groupId in self.__visitedGroups

    def isWaitVisited(self, groupId):
        return groupId in self.__questsToMark

    def visit(self):
        visitedGroups = []
        for groupId, questIds in list(self.__questsToMark.items()):
            for questId in questIds:
                self.__eventsCache.questsProgress.markQuestProgressAsViewed(questId)

            visitedGroups.append(groupId)

        self.__questsToMark.clear()
        if visitedGroups:
            self.__visitedGroups.update(visitedGroups)
            self.onGroupsVisited(visitedGroups)

    def addQuestsToVisited(self, groupID, quests):
        self.__questsToMark[groupID] = quests

    def markQuestForVisitedFromQuestsModel(self, groupID, questsModel):
        idsToVisited = []
        for questModel in questsModel:
            for item in questModel.bonusCondition.getItems():
                if item.getEarned():
                    idsToVisited.append(questModel.getId())

        self.__questsToMark[groupID] = idsToVisited
