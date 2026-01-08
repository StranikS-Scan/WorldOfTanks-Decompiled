# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/tooltips/rank_inactivity_tooltip_model.py
from frameworks.wulf import ViewModel

class RankInactivityTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(RankInactivityTooltipModel, self).__init__(properties=properties, commands=commands)

    def getRankInactivityCount(self):
        return self._getNumber(0)

    def setRankInactivityCount(self, value):
        self._setNumber(0, value)

    def getRankInactivityPointsCount(self):
        return self._getNumber(1)

    def setRankInactivityPointsCount(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(RankInactivityTooltipModel, self)._initialize()
        self._addNumberProperty('rankInactivityCount', -1)
        self._addNumberProperty('rankInactivityPointsCount', 0)
