# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/daily_widget_view_model.py
from frameworks.wulf import ViewModel

class DailyWidgetViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(DailyWidgetViewModel, self).__init__(properties=properties, commands=commands)

    def getDailyBonus(self):
        return self._getNumber(0)

    def setDailyBonus(self, value):
        self._setNumber(0, value)

    def getTimer(self):
        return self._getNumber(1)

    def setTimer(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(DailyWidgetViewModel, self)._initialize()
        self._addNumberProperty('dailyBonus', 0)
        self._addNumberProperty('timer', 0)
