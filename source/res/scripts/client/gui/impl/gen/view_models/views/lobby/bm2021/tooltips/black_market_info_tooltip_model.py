# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/bm2021/tooltips/black_market_info_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.bm2021.tooltips.currency_model import CurrencyModel

class BlackMarketInfoTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BlackMarketInfoTooltipModel, self).__init__(properties=properties, commands=commands)

    def getSlotsNumber(self):
        return self._getNumber(0)

    def setSlotsNumber(self, value):
        self._setNumber(0, value)

    def getVehicleList(self):
        return self._getArray(1)

    def setVehicleList(self, value):
        self._setArray(1, value)

    def getPrices(self):
        return self._getArray(2)

    def setPrices(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(BlackMarketInfoTooltipModel, self)._initialize()
        self._addNumberProperty('slotsNumber', 0)
        self._addArrayProperty('vehicleList', Array())
        self._addArrayProperty('prices', Array())
