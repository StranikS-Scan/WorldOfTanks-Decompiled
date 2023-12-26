# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/advent_calendar/advent_calendar_progression_rewards_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.advent_calendar.advent_calendar_progression_reward_item_view_model import AdventCalendarProgressionRewardItemViewModel

class AdventCalendarProgressionRewardsViewModel(ViewModel):
    __slots__ = ('onProgressionRewardCompleted',)

    def __init__(self, properties=2, commands=1):
        super(AdventCalendarProgressionRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getIsCompleted(self):
        return self._getBool(0)

    def setIsCompleted(self, value):
        self._setBool(0, value)

    def getRewards(self):
        return self._getArray(1)

    def setRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getRewardsType():
        return AdventCalendarProgressionRewardItemViewModel

    def _initialize(self):
        super(AdventCalendarProgressionRewardsViewModel, self)._initialize()
        self._addBoolProperty('isCompleted', False)
        self._addArrayProperty('rewards', Array())
        self.onProgressionRewardCompleted = self._addCommand('onProgressionRewardCompleted')
