# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/reward_path_difficulty_view_model.py
from frameworks.wulf import Array, ViewModel
from last_stand.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel

class RewardPathDifficultyViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(RewardPathDifficultyViewModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getIsLocked(self):
        return self._getBool(1)

    def setIsLocked(self, value):
        self._setBool(1, value)

    def getIsSelected(self):
        return self._getBool(2)

    def setIsSelected(self, value):
        self._setBool(2, value)

    def getIsCompleted(self):
        return self._getBool(3)

    def setIsCompleted(self, value):
        self._setBool(3, value)

    def getAggregatedRewards(self):
        return self._getArray(4)

    def setAggregatedRewards(self, value):
        self._setArray(4, value)

    @staticmethod
    def getAggregatedRewardsType():
        return BonusItemViewModel

    def _initialize(self):
        super(RewardPathDifficultyViewModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addBoolProperty('isLocked', False)
        self._addBoolProperty('isSelected', False)
        self._addBoolProperty('isCompleted', False)
        self._addArrayProperty('aggregatedRewards', Array())
