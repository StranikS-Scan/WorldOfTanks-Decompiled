# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/tooltips/rent_icon_tooltip_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_model import PriceModel

class RentIconTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(RentIconTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return PriceModel

    def getRentDays(self):
        return self._getNumber(1)

    def setRentDays(self, value):
        self._setNumber(1, value)

    def getDaysTotal(self):
        return self._getNumber(2)

    def setDaysTotal(self, value):
        self._setNumber(2, value)

    def getTimeLeft(self):
        return self._getString(3)

    def setTimeLeft(self, value):
        self._setString(3, value)

    def getIsTestDriveMode(self):
        return self._getBool(4)

    def setIsTestDriveMode(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(RentIconTooltipViewModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addNumberProperty('rentDays', 0)
        self._addNumberProperty('daysTotal', 0)
        self._addStringProperty('timeLeft', '')
        self._addBoolProperty('isTestDriveMode', False)
