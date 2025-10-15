# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/seniority_awards/tooltips/seniority_awards_compensation_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.seniority_awards.main_reward_bonus_model import MainRewardBonusModel

class SeniorityAwardsCompensationTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(SeniorityAwardsCompensationTooltipModel, self).__init__(properties=properties, commands=commands)

    def getItemBefore(self):
        return self._getArray(0)

    def setItemBefore(self, value):
        self._setArray(0, value)

    @staticmethod
    def getItemBeforeType():
        return MainRewardBonusModel

    def getItemAfter(self):
        return self._getArray(1)

    def setItemAfter(self, value):
        self._setArray(1, value)

    @staticmethod
    def getItemAfterType():
        return MainRewardBonusModel

    def _initialize(self):
        super(SeniorityAwardsCompensationTooltipModel, self)._initialize()
        self._addArrayProperty('itemBefore', Array())
        self._addArrayProperty('itemAfter', Array())
