# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_event_portals_base.py
from frameworks.wulf import ViewModel

class WtEventPortalsBase(ViewModel):
    __slots__ = ('onBuyButtonClick', 'onClose')

    def __init__(self, properties=7, commands=2):
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

    def getPortalTankName(self):
        return self._getString(3)

    def setPortalTankName(self, value):
        self._setString(3, value)

    def getDiscount(self):
        return self._getNumber(4)

    def setDiscount(self, value):
        self._setNumber(4, value)

    def getDiscountTokenCount(self):
        return self._getNumber(5)

    def setDiscountTokenCount(self, value):
        self._setNumber(5, value)

    def getMaxDiscountTokenCount(self):
        return self._getNumber(6)

    def setMaxDiscountTokenCount(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(WtEventPortalsBase, self)._initialize()
        self._addBoolProperty('isBoxesEnabled', True)
        self._addNumberProperty('availableLootBoxesPurchase', -1)
        self._addBoolProperty('isPortalTankBought', False)
        self._addStringProperty('portalTankName', '')
        self._addNumberProperty('discount', 0)
        self._addNumberProperty('discountTokenCount', 0)
        self._addNumberProperty('maxDiscountTokenCount', 0)
        self.onBuyButtonClick = self._addCommand('onBuyButtonClick')
        self.onClose = self._addCommand('onClose')
