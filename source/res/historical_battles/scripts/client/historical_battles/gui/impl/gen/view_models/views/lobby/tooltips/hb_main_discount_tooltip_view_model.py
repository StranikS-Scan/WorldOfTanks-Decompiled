# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/tooltips/hb_main_discount_tooltip_view_model.py
from frameworks.wulf import ViewModel

class HbMainDiscountTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(HbMainDiscountTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getMaxDiscountCount(self):
        return self._getNumber(0)

    def setMaxDiscountCount(self, value):
        self._setNumber(0, value)

    def getCurrentDiscountCount(self):
        return self._getNumber(1)

    def setCurrentDiscountCount(self, value):
        self._setNumber(1, value)

    def getCurrentDiscountPercent(self):
        return self._getNumber(2)

    def setCurrentDiscountPercent(self, value):
        self._setNumber(2, value)

    def getIcon(self):
        return self._getString(3)

    def setIcon(self, value):
        self._setString(3, value)

    def getVehicleName(self):
        return self._getString(4)

    def setVehicleName(self, value):
        self._setString(4, value)

    def getVehicleLvl(self):
        return self._getNumber(5)

    def setVehicleLvl(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(HbMainDiscountTooltipViewModel, self)._initialize()
        self._addNumberProperty('maxDiscountCount', 0)
        self._addNumberProperty('currentDiscountCount', 0)
        self._addNumberProperty('currentDiscountPercent', 0)
        self._addStringProperty('icon', '')
        self._addStringProperty('vehicleName', '')
        self._addNumberProperty('vehicleLvl', 0)
