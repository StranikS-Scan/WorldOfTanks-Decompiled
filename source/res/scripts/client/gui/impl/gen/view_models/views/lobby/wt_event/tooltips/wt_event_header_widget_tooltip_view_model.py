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

    def __init__(self, properties=5, commands=0):
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

    def getStampsForNextStage(self):
        return self._getNumber(3)

    def setStampsForNextStage(self, value):
        self._setNumber(3, value)

    def getPerformanceRisk(self):
        return PerformanceRisk(self._getNumber(4))

    def setPerformanceRisk(self, value):
        self._setNumber(4, value.value)

    def _initialize(self):
        super(WtEventHeaderWidgetTooltipViewModel, self)._initialize()
        self._addStringProperty('daysLeft', '')
        self._addNumberProperty('commonCurrent', -1)
        self._addNumberProperty('commonTotal', -1)
        self._addNumberProperty('stampsForNextStage', -1)
        self._addNumberProperty('performanceRisk')
