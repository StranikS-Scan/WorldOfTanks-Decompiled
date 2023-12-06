# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/guaranteed_reward_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class GuaranteedRewardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(GuaranteedRewardModel, self).__init__(properties=properties, commands=commands)

    def getLevelsRange(self):
        return self._getArray(0)

    def setLevelsRange(self, value):
        self._setArray(0, value)

    @staticmethod
    def getLevelsRangeType():
        return int

    def getBoxesUntilGuaranteedReward(self):
        return self._getNumber(1)

    def setBoxesUntilGuaranteedReward(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(GuaranteedRewardModel, self)._initialize()
        self._addArrayProperty('levelsRange', Array())
        self._addNumberProperty('boxesUntilGuaranteedReward', 0)
