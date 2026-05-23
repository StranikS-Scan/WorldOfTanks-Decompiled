# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/summer_sale/summer_sale_tokens_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.impl.gen.view_models.views.lobby.summer_sale.price_model import PriceModel

class SummerSaleTokensBonusModel(TokenBonusModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(SummerSaleTokensBonusModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(11)

    @staticmethod
    def getPriceType():
        return PriceModel

    def getProductCode(self):
        return self._getString(12)

    def setProductCode(self, value):
        self._setString(12, value)

    def getInInventory(self):
        return self._getBool(13)

    def setInInventory(self, value):
        self._setBool(13, value)

    def _initialize(self):
        super(SummerSaleTokensBonusModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addStringProperty('productCode', '')
        self._addBoolProperty('inInventory', False)
