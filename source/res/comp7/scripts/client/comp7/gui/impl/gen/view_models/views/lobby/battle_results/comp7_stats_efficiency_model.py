# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/battle_results/comp7_stats_efficiency_model.py
from gui.impl.gen.view_models.views.lobby.battle_results.stats_efficiency_model import StatsEfficiencyModel

class Comp7StatsEfficiencyModel(StatsEfficiencyModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(Comp7StatsEfficiencyModel, self).__init__(properties=properties, commands=commands)

    def getPrestigePoints(self):
        return self._getNumber(3)

    def setPrestigePoints(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(Comp7StatsEfficiencyModel, self)._initialize()
        self._addNumberProperty('prestigePoints', 0)
