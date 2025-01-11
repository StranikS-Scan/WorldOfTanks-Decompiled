# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/progression/level_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.paragons.progression.reward_model import RewardModel

class LevelModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(LevelModel, self).__init__(properties=properties, commands=commands)

    def getNumber(self):
        return self._getNumber(0)

    def setNumber(self, value):
        self._setNumber(0, value)

    def getMaxPoints(self):
        return self._getNumber(1)

    def setMaxPoints(self, value):
        self._setNumber(1, value)

    def getMainRewards(self):
        return self._getArray(2)

    def setMainRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getMainRewardsType():
        return RewardModel

    def getEqualRewards(self):
        return self._getArray(3)

    def setEqualRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getEqualRewardsType():
        return RewardModel

    def _initialize(self):
        super(LevelModel, self)._initialize()
        self._addNumberProperty('number', 1)
        self._addNumberProperty('maxPoints', 0)
        self._addArrayProperty('mainRewards', Array())
        self._addArrayProperty('equalRewards', Array())
