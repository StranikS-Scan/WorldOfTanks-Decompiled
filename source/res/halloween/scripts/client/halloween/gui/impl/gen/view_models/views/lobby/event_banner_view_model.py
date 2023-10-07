# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/event_banner_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class PerformanceRiskEnum(Enum):
    LOWRISK = 'lowRisk'
    MEDIUMRISK = 'mediumRisk'
    HIGHRISK = 'highRisk'


class EventBannerViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=8, commands=1):
        super(EventBannerViewModel, self).__init__(properties=properties, commands=commands)

    def getPhaseTime(self):
        return self._getNumber(0)

    def setPhaseTime(self, value):
        self._setNumber(0, value)

    def getEventEndDate(self):
        return self._getNumber(1)

    def setEventEndDate(self, value):
        self._setNumber(1, value)

    def getEventPostStartDate(self):
        return self._getNumber(2)

    def setEventPostStartDate(self, value):
        self._setNumber(2, value)

    def getIsNew(self):
        return self._getBool(3)

    def setIsNew(self, value):
        self._setBool(3, value)

    def getIsPost(self):
        return self._getBool(4)

    def setIsPost(self, value):
        self._setBool(4, value)

    def getPerformanceRisk(self):
        return PerformanceRiskEnum(self._getString(5))

    def setPerformanceRisk(self, value):
        self._setString(5, value.value)

    def getPhase(self):
        return self._getNumber(6)

    def setPhase(self, value):
        self._setNumber(6, value)

    def getPhases(self):
        return self._getNumber(7)

    def setPhases(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(EventBannerViewModel, self)._initialize()
        self._addNumberProperty('phaseTime', 0)
        self._addNumberProperty('eventEndDate', 0)
        self._addNumberProperty('eventPostStartDate', 0)
        self._addBoolProperty('isNew', False)
        self._addBoolProperty('isPost', False)
        self._addStringProperty('performanceRisk')
        self._addNumberProperty('phase', 0)
        self._addNumberProperty('phases', 0)
        self.onClick = self._addCommand('onClick')
