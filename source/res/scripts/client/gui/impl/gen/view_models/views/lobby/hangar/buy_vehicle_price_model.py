# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/buy_vehicle_price_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencyViewModel

class BuyVehiclePriceModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BuyVehiclePriceModel, self).__init__(properties=properties, commands=commands)

    def getTooltipKey(self):
        return self._getString(0)

    def setTooltipKey(self, value):
        self._setString(0, value)

    def getPrice(self):
        return self._getArray(1)

    def setPrice(self, value):
        self._setArray(1, value)

    @staticmethod
    def getPriceType():
        return CurrencyViewModel

    def _initialize(self):
        super(BuyVehiclePriceModel, self)._initialize()
        self._addStringProperty('tooltipKey', '')
        self._addArrayProperty('price', Array())
