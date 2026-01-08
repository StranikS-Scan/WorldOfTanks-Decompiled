# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/tooltips/wins_indicator_tooltip_model.py
from comp7.gui.impl.gen.view_models.views.lobby.enums import StatisticsMode
from frameworks.wulf import ViewModel

class WinsIndicatorTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(WinsIndicatorTooltipModel, self).__init__(properties=properties, commands=commands)

    def getStatisticsMode(self):
        return StatisticsMode(self._getNumber(0))

    def setStatisticsMode(self, value):
        self._setNumber(0, value.value)

    def getWinRate(self):
        return self._getReal(1)

    def setWinRate(self, value):
        self._setReal(1, value)

    def getWinsCount(self):
        return self._getNumber(2)

    def setWinsCount(self, value):
        self._setNumber(2, value)

    def getLossCount(self):
        return self._getNumber(3)

    def setLossCount(self, value):
        self._setNumber(3, value)

    def getDrawCount(self):
        return self._getNumber(4)

    def setDrawCount(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(WinsIndicatorTooltipModel, self)._initialize()
        self._addNumberProperty('statisticsMode')
        self._addRealProperty('winRate', 0.0)
        self._addNumberProperty('winsCount', 0)
        self._addNumberProperty('lossCount', 0)
        self._addNumberProperty('drawCount', 0)
