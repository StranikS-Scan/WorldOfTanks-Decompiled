# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/achievements/tooltips/battles_kpi_tooltip_view_model.py
from frameworks.wulf import ViewModel

class BattlesKpiTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(BattlesKpiTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getCountOfBattles(self):
        return self._getString(0)

    def setCountOfBattles(self, value):
        self._setString(0, value)

    def getWins(self):
        return self._getString(1)

    def setWins(self, value):
        self._setString(1, value)

    def getDefeat(self):
        return self._getString(2)

    def setDefeat(self, value):
        self._setString(2, value)

    def getDraws(self):
        return self._getString(3)

    def setDraws(self, value):
        self._setString(3, value)

    def getWinsPercent(self):
        return self._getString(4)

    def setWinsPercent(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(BattlesKpiTooltipViewModel, self)._initialize()
        self._addStringProperty('countOfBattles', '')
        self._addStringProperty('wins', '')
        self._addStringProperty('defeat', '')
        self._addStringProperty('draws', '')
        self._addStringProperty('winsPercent', '')
