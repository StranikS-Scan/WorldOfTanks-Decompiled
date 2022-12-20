# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/banner_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class PerformanceRiskEnum(IntEnum):
    HIGHRISK = 1
    MEDIUMRISK = 2
    LOWRISK = 3


class BannerViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=4, commands=1):
        super(BannerViewModel, self).__init__(properties=properties, commands=commands)

    def getFrontlineState(self):
        return self._getString(0)

    def setFrontlineState(self, value):
        self._setString(0, value)

    def getPhaseEndDate(self):
        return self._getNumber(1)

    def setPhaseEndDate(self, value):
        self._setNumber(1, value)

    def getRewardsCount(self):
        return self._getNumber(2)

    def setRewardsCount(self, value):
        self._setNumber(2, value)

    def getPerformanceRisk(self):
        return PerformanceRiskEnum(self._getNumber(3))

    def setPerformanceRisk(self, value):
        self._setNumber(3, value.value)

    def _initialize(self):
        super(BannerViewModel, self)._initialize()
        self._addStringProperty('frontlineState', '')
        self._addNumberProperty('phaseEndDate', 0)
        self._addNumberProperty('rewardsCount', 0)
        self._addNumberProperty('performanceRisk')
        self.onClick = self._addCommand('onClick')
