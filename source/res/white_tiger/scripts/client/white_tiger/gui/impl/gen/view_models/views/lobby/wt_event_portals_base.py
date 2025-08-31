# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_event_portals_base.py
from frameworks.wulf import ViewModel

class WtEventPortalsBase(ViewModel):
    __slots__ = ('onBuyButtonClick', 'onClose')

    def __init__(self, properties=10, commands=2):
        super(WtEventPortalsBase, self).__init__(properties=properties, commands=commands)

    def getIsBoxesEnabled(self):
        return self._getBool(0)

    def setIsBoxesEnabled(self, value):
        self._setBool(0, value)

    def getAvailableLootBoxesPurchase(self):
        return self._getNumber(1)

    def setAvailableLootBoxesPurchase(self, value):
        self._setNumber(1, value)

    def getIsPortalTankBought(self):
        return self._getBool(2)

    def setIsPortalTankBought(self, value):
        self._setBool(2, value)

    def getTankName(self):
        return self._getString(3)

    def setTankName(self, value):
        self._setString(3, value)

    def getTankLevel(self):
        return self._getNumber(4)

    def setTankLevel(self, value):
        self._setNumber(4, value)

    def getTankNation(self):
        return self._getString(5)

    def setTankNation(self, value):
        self._setString(5, value)

    def getTankType(self):
        return self._getString(6)

    def setTankType(self, value):
        self._setString(6, value)

    def getDiscount(self):
        return self._getNumber(7)

    def setDiscount(self, value):
        self._setNumber(7, value)

    def getDiscountTokenCount(self):
        return self._getNumber(8)

    def setDiscountTokenCount(self, value):
        self._setNumber(8, value)

    def getMaxDiscountTokenCount(self):
        return self._getNumber(9)

    def setMaxDiscountTokenCount(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(WtEventPortalsBase, self)._initialize()
        self._addBoolProperty('isBoxesEnabled', True)
        self._addNumberProperty('availableLootBoxesPurchase', -1)
        self._addBoolProperty('isPortalTankBought', False)
        self._addStringProperty('tankName', '')
        self._addNumberProperty('tankLevel', 0)
        self._addStringProperty('tankNation', '')
        self._addStringProperty('tankType', '')
        self._addNumberProperty('discount', 0)
        self._addNumberProperty('discountTokenCount', 0)
        self._addNumberProperty('maxDiscountTokenCount', 0)
        self.onBuyButtonClick = self._addCommand('onBuyButtonClick')
        self.onClose = self._addCommand('onClose')
