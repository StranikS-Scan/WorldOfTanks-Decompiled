# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/battle_results/fun_stats_efficiency_param_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class StatsValueType(IntEnum):
    INTEGER = 0
    FLOAT = 1


class FunStatsEfficiencyParamModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(FunStatsEfficiencyParamModel, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return self._getReal(0)

    def setValue(self, value):
        self._setReal(0, value)

    def getParamValueType(self):
        return StatsValueType(self._getNumber(1))

    def setParamValueType(self, value):
        self._setNumber(1, value.value)

    def _initialize(self):
        super(FunStatsEfficiencyParamModel, self)._initialize()
        self._addRealProperty('value', 0.0)
        self._addNumberProperty('paramValueType', StatsValueType.INTEGER.value)
