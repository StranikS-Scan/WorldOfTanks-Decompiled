# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/gui/impl/gen/view_models/views/lobby/views/battle_quests_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.missions.quest_model import QuestModel

class BattleQuestsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(BattleQuestsModel, self).__init__(properties=properties, commands=commands)

    def getTasksBattle(self):
        return self._getArray(0)

    def setTasksBattle(self, value):
        self._setArray(0, value)

    @staticmethod
    def getTasksBattleType():
        return QuestModel

    def getCurrentTimerDate(self):
        return self._getNumber(1)

    def setCurrentTimerDate(self, value):
        self._setNumber(1, value)

    def getShowPrimeTime(self):
        return self._getBool(2)

    def setShowPrimeTime(self, value):
        self._setBool(2, value)

    def getShowEventEnded(self):
        return self._getBool(3)

    def setShowEventEnded(self, value):
        self._setBool(3, value)

    def getMissionsCompletedVisited(self):
        return self._getArray(4)

    def setMissionsCompletedVisited(self, value):
        self._setArray(4, value)

    def _initialize(self):
        super(BattleQuestsModel, self)._initialize()
        self._addArrayProperty('tasksBattle', Array())
        self._addNumberProperty('currentTimerDate', 0)
        self._addBoolProperty('showPrimeTime', False)
        self._addBoolProperty('showEventEnded', False)
        self._addArrayProperty('missionsCompletedVisited', Array())
