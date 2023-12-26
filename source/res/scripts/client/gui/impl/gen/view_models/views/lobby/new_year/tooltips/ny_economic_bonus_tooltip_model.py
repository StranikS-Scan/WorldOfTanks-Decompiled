# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_economic_bonus_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_economic_bonus_model import NyEconomicBonusModel

class NyEconomicBonusTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NyEconomicBonusTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTotalQuestsQuantity(self):
        return self._getNumber(0)

    def setTotalQuestsQuantity(self, value):
        self._setNumber(0, value)

    def getIsMaxBonus(self):
        return self._getBool(1)

    def setIsMaxBonus(self, value):
        self._setBool(1, value)

    def getEconomicBonuses(self):
        return self._getArray(2)

    def setEconomicBonuses(self, value):
        self._setArray(2, value)

    @staticmethod
    def getEconomicBonusesType():
        return NyEconomicBonusModel

    def _initialize(self):
        super(NyEconomicBonusTooltipModel, self)._initialize()
        self._addNumberProperty('totalQuestsQuantity', 0)
        self._addBoolProperty('isMaxBonus', False)
        self._addArrayProperty('economicBonuses', Array())
