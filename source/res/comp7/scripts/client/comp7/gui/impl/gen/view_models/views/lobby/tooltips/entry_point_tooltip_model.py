# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/tooltips/entry_point_tooltip_model.py
from frameworks.wulf import Array, ViewModel
from comp7.gui.impl.gen.view_models.views.lobby.season_model import SeasonModel

class EntryPointTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(EntryPointTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def season(self):
        return self._getViewModel(0)

    @staticmethod
    def getSeasonType():
        return SeasonModel

    def getTimeLeftUntilPrimeTime(self):
        return self._getNumber(1)

    def setTimeLeftUntilPrimeTime(self, value):
        self._setNumber(1, value)

    def getVehicleLevels(self):
        return self._getArray(2)

    def setVehicleLevels(self, value):
        self._setArray(2, value)

    @staticmethod
    def getVehicleLevelsType():
        return int

    def _initialize(self):
        super(EntryPointTooltipModel, self)._initialize()
        self._addViewModelProperty('season', SeasonModel())
        self._addNumberProperty('timeLeftUntilPrimeTime', 0)
        self._addArrayProperty('vehicleLevels', Array())
