# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/quests/vehicle_quest_info.py
import typing
from gui.Scaleform.genConsts.HANGAR_HEADER_QUESTS import HANGAR_HEADER_QUESTS
from helpers import dependency
from skeletons.gui.game_control import IQuestsController

class VehicleQuestInfo(object):
    __slots__ = ('_vehicle', '_allHBQuestsCount', '_questsCount', '_availableQuests', '_availableQuestsCount', '_completedQuestsCount')
    _questController = dependency.descriptor(IQuestsController)

    def __init__(self, vehicle):
        self._vehicle = vehicle

    def init(self):
        quests = self.__getSortedQuests()
        self._allHBQuestsCount = len(self.__getAllHBQuests())
        self._availableQuests = [ q for q in quests if q.isStarted() ]
        completedQuests = [ q for q in self._availableQuests if q.isCompleted() ]
        self._questsCount = len(quests)
        self._availableQuestsCount = len(self._availableQuests)
        self._completedQuestsCount = len(completedQuests)

    def isAllCompleted(self):
        return self._availableQuestsCount == self._completedQuestsCount != 0

    def isAnyAvailable(self):
        return self._availableQuestsCount != 0

    def isEmptyConfig(self):
        return self.__getAllHBQuestsCount() == 0

    def getUncompletedCount(self):
        return self._availableQuestsCount - self._completedQuestsCount

    def getAvailableQuests(self):
        return self._availableQuests

    def __getAllHBQuestsCount(self):
        return self._allHBQuestsCount

    def __getAllHBQuests(self):
        quests = [ q for q in self._questController.getAllAvailableQuests() if q.getGroupID() == HANGAR_HEADER_QUESTS.QUEST_GROUP_HB_BATTLE and q.isStarted() ]
        return quests

    def __getSortedQuests(self):

        def sortQuests(quest):
            return quest.getUserName()

        quests = [ q for q in self._questController.getQuestForVehicle(self._vehicle) if q.getGroupID() == HANGAR_HEADER_QUESTS.QUEST_GROUP_HB_BATTLE ]
        return sorted(quests, key=sortQuests)
