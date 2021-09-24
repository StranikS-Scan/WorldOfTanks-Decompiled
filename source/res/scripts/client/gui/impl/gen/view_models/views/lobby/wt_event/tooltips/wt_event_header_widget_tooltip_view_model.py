# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/tooltips/wt_event_header_widget_tooltip_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class PerformanceRisk(IntEnum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class WtEventHeaderWidgetTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(WtEventHeaderWidgetTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getDaysLeft(self):
        return self._getString(0)

    def setDaysLeft(self, value):
        self._setString(0, value)

    def getCommonCurrent(self):
        return self._getNumber(1)

    def setCommonCurrent(self, value):
        self._setNumber(1, value)

    def getCommonTotal(self):
        return self._getNumber(2)

    def setCommonTotal(self, value):
        self._setNumber(2, value)

    def getBossCurrent(self):
        return self._getNumber(3)

    def setBossCurrent(self, value):
        self._setNumber(3, value)

    def getBossTotal(self):
        return self._getNumber(4)

    def setBossTotal(self, value):
        self._setNumber(4, value)

    def getHunterCurrent(self):
        return self._getNumber(5)

    def setHunterCurrent(self, value):
        self._setNumber(5, value)

    def getHunterTotal(self):
        return self._getNumber(6)

    def setHunterTotal(self, value):
        self._setNumber(6, value)

    def getNextReward(self):
        return self._getNumber(7)

    def setNextReward(self, value):
        self._setNumber(7, value)

    def getPerformanceRisk(self):
        return PerformanceRisk(self._getNumber(8))

    def setPerformanceRisk(self, value):
        self._setNumber(8, value.value)

    def _initialize(self):
        super(WtEventHeaderWidgetTooltipViewModel, self)._initialize()
        self._addStringProperty('daysLeft', '')
        self._addNumberProperty('commonCurrent', -1)
        self._addNumberProperty('commonTotal', -1)
        self._addNumberProperty('bossCurrent', -1)
        self._addNumberProperty('bossTotal', -1)
        self._addNumberProperty('hunterCurrent', -1)
        self._addNumberProperty('hunterTotal', -1)
        self._addNumberProperty('nextReward', -1)
        self._addNumberProperty('performanceRisk')
