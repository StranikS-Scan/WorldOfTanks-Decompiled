# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/tooltips/probability_guaranteed_reward_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class ProbabilityGuaranteedRewardTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(ProbabilityGuaranteedRewardTooltipModel, self).__init__(properties=properties, commands=commands)

    def getGuaranteedFrequencies(self):
        return self._getArray(0)

    def setGuaranteedFrequencies(self, value):
        self._setArray(0, value)

    @staticmethod
    def getGuaranteedFrequenciesType():
        return int

    def _initialize(self):
        super(ProbabilityGuaranteedRewardTooltipModel, self)._initialize()
        self._addArrayProperty('guaranteedFrequencies', Array())
