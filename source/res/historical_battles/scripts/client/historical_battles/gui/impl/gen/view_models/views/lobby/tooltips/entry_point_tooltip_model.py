# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/tooltips/entry_point_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class PerformanceRiskEnum(Enum):
    LOWRISK = 'lowRisk'
    MEDIUMRISK = 'mediumRisk'
    HIGHRISK = 'highRisk'


class EntryPointTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(EntryPointTooltipModel, self).__init__(properties=properties, commands=commands)

    def getIsHardDisabled(self):
        return self._getBool(0)

    def setIsHardDisabled(self, value):
        self._setBool(0, value)

    def getEventStartDate(self):
        return self._getNumber(1)

    def setEventStartDate(self, value):
        self._setNumber(1, value)

    def getEventEndDate(self):
        return self._getNumber(2)

    def setEventEndDate(self, value):
        self._setNumber(2, value)

    def getPerformanceRisk(self):
        return PerformanceRiskEnum(self._getString(3))

    def setPerformanceRisk(self, value):
        self._setString(3, value.value)

    def _initialize(self):
        super(EntryPointTooltipModel, self)._initialize()
        self._addBoolProperty('isHardDisabled', False)
        self._addNumberProperty('eventStartDate', 0)
        self._addNumberProperty('eventEndDate', 0)
        self._addStringProperty('performanceRisk')
