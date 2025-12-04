# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_pet_overview_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_pet_indicator_model import NyPetIndicatorModel

class NyPetOverviewTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(NyPetOverviewTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCurrentBonus(self):
        return self._getNumber(0)

    def setCurrentBonus(self, value):
        self._setNumber(0, value)

    def getMinBonus(self):
        return self._getNumber(1)

    def setMinBonus(self, value):
        self._setNumber(1, value)

    def getMaxBonus(self):
        return self._getNumber(2)

    def setMaxBonus(self, value):
        self._setNumber(2, value)

    def getMailsAmount(self):
        return self._getNumber(3)

    def setMailsAmount(self, value):
        self._setNumber(3, value)

    def getIsLeaderboard(self):
        return self._getBool(4)

    def setIsLeaderboard(self, value):
        self._setBool(4, value)

    def getIndicators(self):
        return self._getArray(5)

    def setIndicators(self, value):
        self._setArray(5, value)

    @staticmethod
    def getIndicatorsType():
        return NyPetIndicatorModel

    def _initialize(self):
        super(NyPetOverviewTooltipModel, self)._initialize()
        self._addNumberProperty('currentBonus', 0)
        self._addNumberProperty('minBonus', 0)
        self._addNumberProperty('maxBonus', 0)
        self._addNumberProperty('mailsAmount', 0)
        self._addBoolProperty('isLeaderboard', True)
        self._addArrayProperty('indicators', Array())
