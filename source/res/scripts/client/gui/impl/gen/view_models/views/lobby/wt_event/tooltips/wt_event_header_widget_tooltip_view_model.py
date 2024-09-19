# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/tooltips/wt_event_header_widget_tooltip_view_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class PerformanceRisk(IntEnum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class WtEventHeaderWidgetTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(WtEventHeaderWidgetTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getTimeLeft(self):
        return self._getNumber(0)

    def setTimeLeft(self, value):
        self._setNumber(0, value)

    def getStampsCurrent(self):
        return self._getNumber(1)

    def setStampsCurrent(self, value):
        self._setNumber(1, value)

    def getStampsMax(self):
        return self._getNumber(2)

    def setStampsMax(self, value):
        self._setNumber(2, value)

    def getIsProgressionCompleted(self):
        return self._getBool(3)

    def setIsProgressionCompleted(self, value):
        self._setBool(3, value)

    def getStageCurrent(self):
        return self._getNumber(4)

    def setStageCurrent(self, value):
        self._setNumber(4, value)

    def getPerformanceRisk(self):
        return PerformanceRisk(self._getNumber(5))

    def setPerformanceRisk(self, value):
        self._setNumber(5, value.value)

    def getRewards(self):
        return self._getArray(6)

    def setRewards(self, value):
        self._setArray(6, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def getCommonCurrent(self):
        return self._getNumber(7)

    def setCommonCurrent(self, value):
        self._setNumber(7, value)

    def getCommonTotal(self):
        return self._getNumber(8)

    def setCommonTotal(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(WtEventHeaderWidgetTooltipViewModel, self)._initialize()
        self._addNumberProperty('timeLeft', 0)
        self._addNumberProperty('stampsCurrent', 0)
        self._addNumberProperty('stampsMax', 20)
        self._addBoolProperty('isProgressionCompleted', False)
        self._addNumberProperty('stageCurrent', 0)
        self._addNumberProperty('performanceRisk')
        self._addArrayProperty('rewards', Array())
        self._addNumberProperty('commonCurrent', -1)
        self._addNumberProperty('commonTotal', -1)
