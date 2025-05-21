# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/event_banner_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class PerformanceRiskEnum(Enum):
    LOWRISK = 'lowRisk'
    MEDIUMRISK = 'mediumRisk'
    HIGHRISK = 'highRisk'


class EventBannerViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=5, commands=1):
        super(EventBannerViewModel, self).__init__(properties=properties, commands=commands)

    def getDate(self):
        return self._getNumber(0)

    def setDate(self, value):
        self._setNumber(0, value)

    def getEndDate(self):
        return self._getNumber(1)

    def setEndDate(self, value):
        self._setNumber(1, value)

    def getIsNew(self):
        return self._getBool(2)

    def setIsNew(self, value):
        self._setBool(2, value)

    def getIsKingRewardReceive(self):
        return self._getBool(3)

    def setIsKingRewardReceive(self, value):
        self._setBool(3, value)

    def getPerformanceRisk(self):
        return PerformanceRiskEnum(self._getString(4))

    def setPerformanceRisk(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(EventBannerViewModel, self)._initialize()
        self._addNumberProperty('date', 0)
        self._addNumberProperty('endDate', 0)
        self._addBoolProperty('isNew', False)
        self._addBoolProperty('isKingRewardReceive', False)
        self._addStringProperty('performanceRisk')
        self.onClick = self._addCommand('onClick')
