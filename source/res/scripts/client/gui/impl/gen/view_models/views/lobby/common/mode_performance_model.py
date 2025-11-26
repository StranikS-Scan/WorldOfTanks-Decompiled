# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/mode_performance_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class PerformanceRiskEnum(Enum):
    LOWRISK = 'lowRisk'
    MEDIUMRISK = 'mediumRisk'
    HIGHRISK = 'highRisk'


class ModePerformanceModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ModePerformanceModel, self).__init__(properties=properties, commands=commands)

    def getShowPerfRisk(self):
        return self._getBool(0)

    def setShowPerfRisk(self, value):
        self._setBool(0, value)

    def getPerformanceRisk(self):
        return PerformanceRiskEnum(self._getString(1))

    def setPerformanceRisk(self, value):
        self._setString(1, value.value)

    def _initialize(self):
        super(ModePerformanceModel, self)._initialize()
        self._addBoolProperty('showPerfRisk', False)
        self._addStringProperty('performanceRisk')
