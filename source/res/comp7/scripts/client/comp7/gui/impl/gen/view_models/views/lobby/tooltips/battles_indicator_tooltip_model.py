# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/tooltips/battles_indicator_tooltip_model.py
from comp7.gui.impl.gen.view_models.views.lobby.enums import StatisticsMode
from frameworks.wulf import ViewModel

class BattlesIndicatorTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BattlesIndicatorTooltipModel, self).__init__(properties=properties, commands=commands)

    def getStatisticsMode(self):
        return StatisticsMode(self._getNumber(0))

    def setStatisticsMode(self, value):
        self._setNumber(0, value.value)

    def getSoloBattlesCount(self):
        return self._getNumber(1)

    def setSoloBattlesCount(self, value):
        self._setNumber(1, value)

    def getSuperPlatoonBattlesCount(self):
        return self._getNumber(2)

    def setSuperPlatoonBattlesCount(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(BattlesIndicatorTooltipModel, self)._initialize()
        self._addNumberProperty('statisticsMode')
        self._addNumberProperty('soloBattlesCount', 0)
        self._addNumberProperty('superPlatoonBattlesCount', 0)
