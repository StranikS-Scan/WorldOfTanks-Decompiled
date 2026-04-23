# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/tooltips/reward_path_tooltip_view_model.py
from frameworks.wulf import Array
from last_stand.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.reward_path_view_model import RewardPathViewModel

class RewardPathTooltipViewModel(RewardPathViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=1):
        super(RewardPathTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getRewards(self):
        return self._getArray(5)

    def setRewards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getRewardsType():
        return BonusItemViewModel

    def _initialize(self):
        super(RewardPathTooltipViewModel, self)._initialize()
        self._addArrayProperty('rewards', Array())
