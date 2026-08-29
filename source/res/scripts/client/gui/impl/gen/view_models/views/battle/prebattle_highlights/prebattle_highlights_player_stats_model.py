# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/prebattle_highlights/prebattle_highlights_player_stats_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.battle.prebattle_highlights.stats_parameter_model import StatsParameterModel

class PrebattleHighlightsPlayerStatsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(PrebattleHighlightsPlayerStatsModel, self).__init__(properties=properties, commands=commands)

    def getVehId(self):
        return self._getNumber(0)

    def setVehId(self, value):
        self._setNumber(0, value)

    def getStatsParams(self):
        return self._getArray(1)

    def setStatsParams(self, value):
        self._setArray(1, value)

    @staticmethod
    def getStatsParamsType():
        return StatsParameterModel

    def _initialize(self):
        super(PrebattleHighlightsPlayerStatsModel, self)._initialize()
        self._addNumberProperty('vehId', 0)
        self._addArrayProperty('statsParams', Array())
