# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/shop_block_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.halloween.price_model import PriceModel
from gui.impl.gen.view_models.views.lobby.halloween.shop_offer_model import ShopOfferModel

class ShopBlockModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ShopBlockModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    def getOffers(self):
        return self._getArray(1)

    def setOffers(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(ShopBlockModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addArrayProperty('offers', Array())
