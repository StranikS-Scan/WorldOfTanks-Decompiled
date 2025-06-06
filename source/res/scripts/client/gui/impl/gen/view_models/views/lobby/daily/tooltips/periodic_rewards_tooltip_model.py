# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/tooltips/periodic_rewards_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.play_streak.rewards_calendar_item import RewardsCalendarItem

class PeriodicRewardsTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PeriodicRewardsTooltipModel, self).__init__(properties=properties, commands=commands)

    def getStreakLength(self):
        return self._getNumber(0)

    def setStreakLength(self, value):
        self._setNumber(0, value)

    def getDailyWin(self):
        return self._getBool(1)

    def setDailyWin(self, value):
        self._setBool(1, value)

    def getRewardsCalendar(self):
        return self._getArray(2)

    def setRewardsCalendar(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsCalendarType():
        return RewardsCalendarItem

    def _initialize(self):
        super(PeriodicRewardsTooltipModel, self)._initialize()
        self._addNumberProperty('streakLength', 0)
        self._addBoolProperty('dailyWin', False)
        self._addArrayProperty('rewardsCalendar', Array())
