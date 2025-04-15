# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/play_streak/play_streak_tab_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class PlayStreakTabViewModel(ViewModel):
    __slots__ = ('onShowInfo', 'onFinishAnimation')

    def __init__(self, properties=10, commands=2):
        super(PlayStreakTabViewModel, self).__init__(properties=properties, commands=commands)

    def getStreakLength(self):
        return self._getNumber(0)

    def setStreakLength(self, value):
        self._setNumber(0, value)

    def getSkipDayCount(self):
        return self._getNumber(1)

    def setSkipDayCount(self, value):
        self._setNumber(1, value)

    def getRedemptionDayCount(self):
        return self._getNumber(2)

    def setRedemptionDayCount(self, value):
        self._setNumber(2, value)

    def getRedemptionMaxDayCount(self):
        return self._getNumber(3)

    def setRedemptionMaxDayCount(self, value):
        self._setNumber(3, value)

    def getDailyWin(self):
        return self._getBool(4)

    def setDailyWin(self, value):
        self._setBool(4, value)

    def getIsBlocked(self):
        return self._getBool(5)

    def setIsBlocked(self, value):
        self._setBool(5, value)

    def getIsFirstAppearance(self):
        return self._getBool(6)

    def setIsFirstAppearance(self, value):
        self._setBool(6, value)

    def getIsPaused(self):
        return self._getBool(7)

    def setIsPaused(self, value):
        self._setBool(7, value)

    def getIsEnabled(self):
        return self._getBool(8)

    def setIsEnabled(self, value):
        self._setBool(8, value)

    def getBattleTypes(self):
        return self._getArray(9)

    def setBattleTypes(self, value):
        self._setArray(9, value)

    @staticmethod
    def getBattleTypesType():
        return int

    def _initialize(self):
        super(PlayStreakTabViewModel, self)._initialize()
        self._addNumberProperty('streakLength', 0)
        self._addNumberProperty('skipDayCount', 0)
        self._addNumberProperty('redemptionDayCount', 0)
        self._addNumberProperty('redemptionMaxDayCount', 0)
        self._addBoolProperty('dailyWin', False)
        self._addBoolProperty('isBlocked', False)
        self._addBoolProperty('isFirstAppearance', False)
        self._addBoolProperty('isPaused', False)
        self._addBoolProperty('isEnabled', False)
        self._addArrayProperty('battleTypes', Array())
        self.onShowInfo = self._addCommand('onShowInfo')
        self.onFinishAnimation = self._addCommand('onFinishAnimation')
