# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/tooltips/guaranteed_reward_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class GuaranteedRewardTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(GuaranteedRewardTooltipModel, self).__init__(properties=properties, commands=commands)

    def getLevelsRange(self):
        return self._getArray(0)

    def setLevelsRange(self, value):
        self._setArray(0, value)

    @staticmethod
    def getLevelsRangeType():
        return int

    def getGuaranteedFrequency(self):
        return self._getNumber(1)

    def setGuaranteedFrequency(self, value):
        self._setNumber(1, value)

    def getGuaranteedBoxNameKeys(self):
        return self._getArray(2)

    def setGuaranteedBoxNameKeys(self, value):
        self._setArray(2, value)

    @staticmethod
    def getGuaranteedBoxNameKeysType():
        return unicode

    def _initialize(self):
        super(GuaranteedRewardTooltipModel, self)._initialize()
        self._addArrayProperty('levelsRange', Array())
        self._addNumberProperty('guaranteedFrequency', 0)
        self._addArrayProperty('guaranteedBoxNameKeys', Array())
