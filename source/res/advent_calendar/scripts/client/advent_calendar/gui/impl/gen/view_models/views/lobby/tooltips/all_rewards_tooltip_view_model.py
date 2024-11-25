# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/gen/view_models/views/lobby/tooltips/all_rewards_tooltip_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from advent_calendar.gui.impl.gen.view_models.views.lobby.tooltips.bonus_item_view_model import BonusItemViewModel

class AllRewardsTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(AllRewardsTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getRewards(self):
        return self._getArray(0)

    def setRewards(self, value):
        self._setArray(0, value)

    @staticmethod
    def getRewardsType():
        return BonusItemViewModel

    def _initialize(self):
        super(AllRewardsTooltipViewModel, self)._initialize()
        self._addArrayProperty('rewards', Array())
