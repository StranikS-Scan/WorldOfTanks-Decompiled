# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/progression/stage_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.paragons.progression.level_model import LevelModel

class StageModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(StageModel, self).__init__(properties=properties, commands=commands)

    def getNumber(self):
        return self._getNumber(0)

    def setNumber(self, value):
        self._setNumber(0, value)

    def getPoints(self):
        return self._getNumber(1)

    def setPoints(self, value):
        self._setNumber(1, value)

    def getIsCompleted(self):
        return self._getBool(2)

    def setIsCompleted(self, value):
        self._setBool(2, value)

    def getIsAllRewardsClaimed(self):
        return self._getBool(3)

    def setIsAllRewardsClaimed(self, value):
        self._setBool(3, value)

    def getCurrentLevel(self):
        return self._getNumber(4)

    def setCurrentLevel(self, value):
        self._setNumber(4, value)

    def getLevels(self):
        return self._getArray(5)

    def setLevels(self, value):
        self._setArray(5, value)

    @staticmethod
    def getLevelsType():
        return LevelModel

    def _initialize(self):
        super(StageModel, self)._initialize()
        self._addNumberProperty('number', 1)
        self._addNumberProperty('points', 0)
        self._addBoolProperty('isCompleted', False)
        self._addBoolProperty('isAllRewardsClaimed', False)
        self._addNumberProperty('currentLevel', 1)
        self._addArrayProperty('levels', Array())
