# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/battle_results/fun_stats_efficiency_model.py
from frameworks.wulf import Map, ViewModel
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_stats_efficiency_param_model import FunStatsEfficiencyParamModel

class FunStatsEfficiencyModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(FunStatsEfficiencyModel, self).__init__(properties=properties, commands=commands)

    def getParameters(self):
        return self._getMap(0)

    def setParameters(self, value):
        self._setMap(0, value)

    @staticmethod
    def getParametersType():
        return (unicode, FunStatsEfficiencyParamModel)

    def _initialize(self):
        super(FunStatsEfficiencyModel, self)._initialize()
        self._addMapProperty('parameters', Map(unicode, FunStatsEfficiencyParamModel))
