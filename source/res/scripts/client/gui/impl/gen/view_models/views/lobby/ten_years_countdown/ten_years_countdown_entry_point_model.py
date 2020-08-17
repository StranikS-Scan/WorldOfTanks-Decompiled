# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ten_years_countdown/ten_years_countdown_entry_point_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class TenYearsCountdownEntryPointModel(ViewModel):
    __slots__ = ('onActionClick',)

    def __init__(self, properties=7, commands=1):
        super(TenYearsCountdownEntryPointModel, self).__init__(properties=properties, commands=commands)

    def getBlockTitle(self):
        return self._getString(0)

    def setBlockTitle(self, value):
        self._setString(0, value)

    def getTimer(self):
        return self._getString(1)

    def setTimer(self, value):
        self._setString(1, value)

    def getIsTimerPaused(self):
        return self._getBool(2)

    def setIsTimerPaused(self, value):
        self._setBool(2, value)

    def getBalance(self):
        return self._getString(3)

    def setBalance(self, value):
        self._setString(3, value)

    def getCoinIcon(self):
        return self._getResource(4)

    def setCoinIcon(self, value):
        self._setResource(4, value)

    def getTimerText(self):
        return self._getString(5)

    def setTimerText(self, value):
        self._setString(5, value)

    def getIsChina(self):
        return self._getBool(6)

    def setIsChina(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(TenYearsCountdownEntryPointModel, self)._initialize()
        self._addStringProperty('blockTitle', '')
        self._addStringProperty('timer', '')
        self._addBoolProperty('isTimerPaused', False)
        self._addStringProperty('balance', '')
        self._addResourceProperty('coinIcon', R.invalid())
        self._addStringProperty('timerText', '')
        self._addBoolProperty('isChina', False)
        self.onActionClick = self._addCommand('onActionClick')
