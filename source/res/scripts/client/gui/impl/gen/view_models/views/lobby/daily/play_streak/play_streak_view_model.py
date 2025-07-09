# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/play_streak/play_streak_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.views.lobby.play_streak.rewards_calendar_item import RewardsCalendarItem

class PlayStreakViewModel(ViewModel):
    __slots__ = ('onVehiclePreviewClick', 'onShowVehicle', 'onStylePreviewClick')

    def __init__(self, properties=15, commands=3):
        super(PlayStreakViewModel, self).__init__(properties=properties, commands=commands)

    def getStreakLength(self):
        return self._getNumber(0)

    def setStreakLength(self, value):
        self._setNumber(0, value)

    def getSkipDayCount(self):
        return self._getNumber(1)

    def setSkipDayCount(self, value):
        self._setNumber(1, value)

    def getDailyWin(self):
        return self._getBool(2)

    def setDailyWin(self, value):
        self._setBool(2, value)

    def getIsBlocked(self):
        return self._getBool(3)

    def setIsBlocked(self, value):
        self._setBool(3, value)

    def getIsPaused(self):
        return self._getBool(4)

    def setIsPaused(self, value):
        self._setBool(4, value)

    def getIsFirstAppearance(self):
        return self._getBool(5)

    def setIsFirstAppearance(self, value):
        self._setBool(5, value)

    def getIsFirstAppearanceRedemptionDay(self):
        return self._getBool(6)

    def setIsFirstAppearanceRedemptionDay(self, value):
        self._setBool(6, value)

    def getIsLastDayRedemption(self):
        return self._getBool(7)

    def setIsLastDayRedemption(self, value):
        self._setBool(7, value)

    def getRedemptionDayCount(self):
        return self._getNumber(8)

    def setRedemptionDayCount(self, value):
        self._setNumber(8, value)

    def getRedemptionMaxDayCount(self):
        return self._getNumber(9)

    def setRedemptionMaxDayCount(self, value):
        self._setNumber(9, value)

    def getIsEnabled(self):
        return self._getBool(10)

    def setIsEnabled(self, value):
        self._setBool(10, value)

    def getBattleTypes(self):
        return self._getArray(11)

    def setBattleTypes(self, value):
        self._setArray(11, value)

    @staticmethod
    def getBattleTypesType():
        return int

    def getRewardsCalendar(self):
        return self._getArray(12)

    def setRewardsCalendar(self, value):
        self._setArray(12, value)

    @staticmethod
    def getRewardsCalendarType():
        return RewardsCalendarItem

    def getTopRewards(self):
        return self._getArray(13)

    def setTopRewards(self, value):
        self._setArray(13, value)

    @staticmethod
    def getTopRewardsType():
        return RewardsCalendarItem

    def getPeriodicRewards(self):
        return self._getArray(14)

    def setPeriodicRewards(self, value):
        self._setArray(14, value)

    @staticmethod
    def getPeriodicRewardsType():
        return IconBonusModel

    def _initialize(self):
        super(PlayStreakViewModel, self)._initialize()
        self._addNumberProperty('streakLength', 0)
        self._addNumberProperty('skipDayCount', 0)
        self._addBoolProperty('dailyWin', False)
        self._addBoolProperty('isBlocked', False)
        self._addBoolProperty('isPaused', False)
        self._addBoolProperty('isFirstAppearance', False)
        self._addBoolProperty('isFirstAppearanceRedemptionDay', False)
        self._addBoolProperty('isLastDayRedemption', False)
        self._addNumberProperty('redemptionDayCount', 0)
        self._addNumberProperty('redemptionMaxDayCount', 0)
        self._addBoolProperty('isEnabled', False)
        self._addArrayProperty('battleTypes', Array())
        self._addArrayProperty('rewardsCalendar', Array())
        self._addArrayProperty('topRewards', Array())
        self._addArrayProperty('periodicRewards', Array())
        self.onVehiclePreviewClick = self._addCommand('onVehiclePreviewClick')
        self.onShowVehicle = self._addCommand('onShowVehicle')
        self.onStylePreviewClick = self._addCommand('onStylePreviewClick')
