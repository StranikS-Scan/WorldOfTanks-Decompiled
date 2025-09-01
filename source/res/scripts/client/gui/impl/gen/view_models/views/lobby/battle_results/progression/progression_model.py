# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/progression/progression_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel

class ProgressionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(ProgressionModel, self).__init__(properties=properties, commands=commands)

    def getDailyQuests(self):
        return self._getArray(0)

    def setDailyQuests(self, value):
        self._setArray(0, value)

    @staticmethod
    def getDailyQuestsType():
        return DailyQuestModel

    def _initialize(self):
        super(ProgressionModel, self)._initialize()
        self._addArrayProperty('dailyQuests', Array())
