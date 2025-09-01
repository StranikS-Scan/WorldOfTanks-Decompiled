# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/level_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel

class LevelModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(LevelModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getLevelPoints(self):
        return self._getNumber(1)

    def setLevelPoints(self, value):
        self._setNumber(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return RewardItemModel

    def _initialize(self):
        super(LevelModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addNumberProperty('levelPoints', 0)
        self._addArrayProperty('rewards', Array())
