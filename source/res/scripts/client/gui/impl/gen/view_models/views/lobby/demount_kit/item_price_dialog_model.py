# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/demount_kit/item_price_dialog_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.demount_kit.item_base_dialog_model import ItemBaseDialogModel

class ItemPriceDialogModel(ItemBaseDialogModel):
    __slots__ = ()

    def __init__(self, properties=16, commands=2):
        super(ItemPriceDialogModel, self).__init__(properties=properties, commands=commands)

    def getPriceDescription(self):
        return self._getResource(12)

    def setPriceDescription(self, value):
        self._setResource(12, value)

    def getItemPrice(self):
        return self._getNumber(13)

    def setItemPrice(self, value):
        self._setNumber(13, value)

    def getCurrencyType(self):
        return self._getString(14)

    def setCurrencyType(self, value):
        self._setString(14, value)

    def getDiscount(self):
        return self._getNumber(15)

    def setDiscount(self, value):
        self._setNumber(15, value)

    def _initialize(self):
        super(ItemPriceDialogModel, self)._initialize()
        self._addResourceProperty('priceDescription', R.invalid())
        self._addNumberProperty('itemPrice', 0)
        self._addStringProperty('currencyType', '')
        self._addNumberProperty('discount', 0)
