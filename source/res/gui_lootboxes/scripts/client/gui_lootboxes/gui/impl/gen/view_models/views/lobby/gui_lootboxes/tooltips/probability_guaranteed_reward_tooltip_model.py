# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/tooltips/probability_guaranteed_reward_tooltip_model.py
from frameworks.wulf import ViewModel

class ProbabilityGuaranteedRewardTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(ProbabilityGuaranteedRewardTooltipModel, self).__init__(properties=properties, commands=commands)

    def getGuaranteedFrequency(self):
        return self._getNumber(0)

    def setGuaranteedFrequency(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(ProbabilityGuaranteedRewardTooltipModel, self)._initialize()
        self._addNumberProperty('guaranteedFrequency', 0)
