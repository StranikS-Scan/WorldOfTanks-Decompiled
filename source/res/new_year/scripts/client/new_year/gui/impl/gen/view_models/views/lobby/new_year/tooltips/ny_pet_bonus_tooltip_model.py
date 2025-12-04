# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_pet_bonus_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_pet_indicator_model import NyPetIndicatorModel

class NyPetBonusTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(NyPetBonusTooltipModel, self).__init__(properties=properties, commands=commands)

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

    def getWasLeaderboardFinished(self):
        return self._getBool(3)

    def setWasLeaderboardFinished(self, value):
        self._setBool(3, value)

    def getIndicators(self):
        return self._getArray(4)

    def setIndicators(self, value):
        self._setArray(4, value)

    @staticmethod
    def getIndicatorsType():
        return NyPetIndicatorModel

    def _initialize(self):
        super(NyPetBonusTooltipModel, self)._initialize()
        self._addNumberProperty('currentBonus', 0)
        self._addNumberProperty('minBonus', 0)
        self._addNumberProperty('maxBonus', 0)
        self._addBoolProperty('wasLeaderboardFinished', False)
        self._addArrayProperty('indicators', Array())
