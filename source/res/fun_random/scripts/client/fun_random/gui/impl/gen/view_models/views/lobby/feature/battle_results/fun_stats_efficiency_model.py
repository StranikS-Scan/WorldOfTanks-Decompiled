# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/battle_results/fun_stats_efficiency_model.py
from gui.impl.gen.view_models.views.lobby.battle_results.stats_efficiency_model import StatsEfficiencyModel

class FunStatsEfficiencyModel(StatsEfficiencyModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(FunStatsEfficiencyModel, self).__init__(properties=properties, commands=commands)

    def getFinishPosition(self):
        return self._getNumber(3)

    def setFinishPosition(self, value):
        self._setNumber(3, value)

    def getFinishTime(self):
        return self._getReal(4)

    def setFinishTime(self, value):
        self._setReal(4, value)

    def getCheckpointsPassed(self):
        return self._getNumber(5)

    def setCheckpointsPassed(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(FunStatsEfficiencyModel, self)._initialize()
        self._addNumberProperty('finishPosition', 0)
        self._addRealProperty('finishTime', 0.0)
        self._addNumberProperty('checkpointsPassed', 0)
