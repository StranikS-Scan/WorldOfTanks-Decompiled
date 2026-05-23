# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/summer_sale/product_model.py
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.summer_sale.price_model import PriceModel

class ProductModel(BonusModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(ProductModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(7)

    @staticmethod
    def getPriceType():
        return PriceModel

    def getProductCode(self):
        return self._getString(8)

    def setProductCode(self, value):
        self._setString(8, value)

    def getInInventory(self):
        return self._getBool(9)

    def setInInventory(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(ProductModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addStringProperty('productCode', '')
        self._addBoolProperty('inInventory', False)
