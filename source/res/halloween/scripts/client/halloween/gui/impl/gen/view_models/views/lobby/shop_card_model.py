# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/shop_card_model.py
from frameworks.wulf import ViewModel

class ShopCardModel(ViewModel):
    __slots__ = ('onGoToShop',)

    def __init__(self, properties=2, commands=1):
        super(ShopCardModel, self).__init__(properties=properties, commands=commands)

    def getStartingPrice(self):
        return self._getNumber(0)

    def setStartingPrice(self, value):
        self._setNumber(0, value)

    def getShopIcon(self):
        return self._getString(1)

    def setShopIcon(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(ShopCardModel, self)._initialize()
        self._addNumberProperty('startingPrice', 0)
        self._addStringProperty('shopIcon', '')
        self.onGoToShop = self._addCommand('onGoToShop')
