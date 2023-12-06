# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_total_bonus_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_multiplier_value import NyMultiplierValue

class NyTotalBonusTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(NyTotalBonusTooltipModel, self).__init__(properties=properties, commands=commands)

    def getPrevBonus(self):
        return self._getReal(0)

    def setPrevBonus(self, value):
        self._setReal(0, value)

    def getCurrentBonus(self):
        return self._getReal(1)

    def setCurrentBonus(self, value):
        self._setReal(1, value)

    def getMaxBonus(self):
        return self._getReal(2)

    def setMaxBonus(self, value):
        self._setReal(2, value)

    def getMultipliersTable(self):
        return self._getArray(3)

    def setMultipliersTable(self, value):
        self._setArray(3, value)

    @staticmethod
    def getMultipliersTableType():
        return NyMultiplierValue

    def _initialize(self):
        super(NyTotalBonusTooltipModel, self)._initialize()
        self._addRealProperty('prevBonus', 0.0)
        self._addRealProperty('currentBonus', 0.0)
        self._addRealProperty('maxBonus', 25)
        self._addArrayProperty('multipliersTable', Array())
