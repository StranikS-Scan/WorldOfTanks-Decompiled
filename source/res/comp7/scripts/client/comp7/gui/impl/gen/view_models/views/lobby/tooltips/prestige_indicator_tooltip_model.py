# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/tooltips/prestige_indicator_tooltip_model.py
from comp7.gui.impl.gen.view_models.views.lobby.enums import StatisticsMode
from frameworks.wulf import ViewModel

class PrestigeIndicatorTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(PrestigeIndicatorTooltipModel, self).__init__(properties=properties, commands=commands)

    def getStatisticsMode(self):
        return StatisticsMode(self._getNumber(0))

    def setStatisticsMode(self, value):
        self._setNumber(0, value.value)

    def getAveragePrestige(self):
        return self._getReal(1)

    def setAveragePrestige(self, value):
        self._setReal(1, value)

    def getRecordPrestige(self):
        return self._getReal(2)

    def setRecordPrestige(self, value):
        self._setReal(2, value)

    def getRecordPrestigeVehicleName(self):
        return self._getString(3)

    def setRecordPrestigeVehicleName(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(PrestigeIndicatorTooltipModel, self)._initialize()
        self._addNumberProperty('statisticsMode')
        self._addRealProperty('averagePrestige', 0.0)
        self._addRealProperty('recordPrestige', 0.0)
        self._addStringProperty('recordPrestigeVehicleName', '')
