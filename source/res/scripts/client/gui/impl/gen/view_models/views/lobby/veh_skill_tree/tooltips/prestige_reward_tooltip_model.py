# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/veh_skill_tree/tooltips/prestige_reward_tooltip_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.veh_skill_tree.tooltips.rewards_slot_tooltip_model import RewardsSlotTooltipModel

class PrestigeRewardTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(PrestigeRewardTooltipModel, self).__init__(properties=properties, commands=commands)

    def getRewards(self):
        return self._getArray(0)

    def setRewards(self, value):
        self._setArray(0, value)

    @staticmethod
    def getRewardsType():
        return RewardsSlotTooltipModel

    def _initialize(self):
        super(PrestigeRewardTooltipModel, self)._initialize()
        self._addArrayProperty('rewards', Array())
