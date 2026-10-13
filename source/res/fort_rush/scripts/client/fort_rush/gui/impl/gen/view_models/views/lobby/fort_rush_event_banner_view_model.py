# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/gen/view_models/views/lobby/fort_rush_event_banner_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class PerformanceRiskEnum(Enum):
    LOWRISK = 'lowRisk'
    MEDIUMRISK = 'mediumRisk'
    HIGHRISK = 'highRisk'


class State(Enum):
    INTRO = 'intro'
    INPROGRESS = 'inProgress'
    FROZEN = 'frozen'


class FortRushEventBannerViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(FortRushEventBannerViewModel, self).__init__(properties=properties, commands=commands)

    def getDate(self):
        return self._getNumber(0)

    def setDate(self, value):
        self._setNumber(0, value)

    def getEndDate(self):
        return self._getNumber(1)

    def setEndDate(self, value):
        self._setNumber(1, value)

    def getPerformanceRisk(self):
        return PerformanceRiskEnum(self._getString(2))

    def setPerformanceRisk(self, value):
        self._setString(2, value.value)

    def getCurLevel(self):
        return self._getNumber(3)

    def setCurLevel(self, value):
        self._setNumber(3, value)

    def getMaxLevel(self):
        return self._getNumber(4)

    def setMaxLevel(self, value):
        self._setNumber(4, value)

    def getCurPoints(self):
        return self._getNumber(5)

    def setCurPoints(self, value):
        self._setNumber(5, value)

    def getMaxPoints(self):
        return self._getNumber(6)

    def setMaxPoints(self, value):
        self._setNumber(6, value)

    def getState(self):
        return State(self._getString(7))

    def setState(self, value):
        self._setString(7, value.value)

    def _initialize(self):
        super(FortRushEventBannerViewModel, self)._initialize()
        self._addNumberProperty('date', 0)
        self._addNumberProperty('endDate', 0)
        self._addStringProperty('performanceRisk')
        self._addNumberProperty('curLevel', 0)
        self._addNumberProperty('maxLevel', 0)
        self._addNumberProperty('curPoints', 0)
        self._addNumberProperty('maxPoints', 0)
        self._addStringProperty('state')
