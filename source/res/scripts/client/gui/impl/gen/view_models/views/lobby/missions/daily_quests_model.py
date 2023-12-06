# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/missions/daily_quests_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel
from gui.impl.gen.view_models.views.lobby.missions.missions_completed_visited_model import MissionsCompletedVisitedModel

class DailyQuestsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(DailyQuestsModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(0)

    def setTitle(self, value):
        self._setResource(0, value)

    def getQuests(self):
        return self._getArray(1)

    def setQuests(self, value):
        self._setArray(1, value)

    @staticmethod
    def getQuestsType():
        return DailyQuestModel

    def getIsEnabled(self):
        return self._getBool(2)

    def setIsEnabled(self, value):
        self._setBool(2, value)

    def getRerollEnabled(self):
        return self._getBool(3)

    def setRerollEnabled(self, value):
        self._setBool(3, value)

    def getRerollCountDown(self):
        return self._getNumber(4)

    def setRerollCountDown(self, value):
        self._setNumber(4, value)

    def getRerollTimeout(self):
        return self._getNumber(5)

    def setRerollTimeout(self, value):
        self._setNumber(5, value)

    def getBonusMissionVisited(self):
        return self._getBool(6)

    def setBonusMissionVisited(self, value):
        self._setBool(6, value)

    def getMissionsCompletedVisited(self):
        return self._getArray(7)

    def setMissionsCompletedVisited(self, value):
        self._setArray(7, value)

    @staticmethod
    def getMissionsCompletedVisitedType():
        return MissionsCompletedVisitedModel

    def getSyncInitiator(self):
        return self._getNumber(8)

    def setSyncInitiator(self, value):
        self._setNumber(8, value)

    def getPlayNYQuestLootboxAnimation(self):
        return self._getBool(9)

    def setPlayNYQuestLootboxAnimation(self, value):
        self._setBool(9, value)

    def getPlayNYBonusQuestLootboxAnimation(self):
        return self._getBool(10)

    def setPlayNYBonusQuestLootboxAnimation(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(DailyQuestsModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addArrayProperty('quests', Array())
        self._addBoolProperty('isEnabled', False)
        self._addBoolProperty('rerollEnabled', False)
        self._addNumberProperty('rerollCountDown', 0)
        self._addNumberProperty('rerollTimeout', 0)
        self._addBoolProperty('bonusMissionVisited', False)
        self._addArrayProperty('missionsCompletedVisited', Array())
        self._addNumberProperty('syncInitiator', 0)
        self._addBoolProperty('playNYQuestLootboxAnimation', False)
        self._addBoolProperty('playNYBonusQuestLootboxAnimation', False)
