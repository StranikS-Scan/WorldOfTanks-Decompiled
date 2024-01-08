# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/meta_view/pages/shop_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.base_product_model import BaseProductModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.rank_discount_model import RankDiscountModel

class Rank(IntEnum):
    FIRST = 6
    SECOND = 5
    THIRD = 4
    FOURTH = 3
    FIFTH = 2
    SIXTH = 1


class ShopState(IntEnum):
    INITIAL = 0
    SUCCESS = 1
    ERROR = 2


class ShopModel(ViewModel):
    __slots__ = ('onProductSeen', 'onProductSelect', 'onProductPurchase', 'onProductRestore', 'onGoToHangar', 'onGoToPreview', 'onGoToCustomization', 'onAddToVehicleCompare', 'onMouseOver3dScene', 'onMoveSpace')

    def __init__(self, properties=8, commands=10):
        super(ShopModel, self).__init__(properties=properties, commands=commands)

    def getShopState(self):
        return ShopState(self._getNumber(0))

    def setShopState(self, value):
        self._setNumber(0, value.value)

    def getIsVehiclesCompareEnabled(self):
        return self._getBool(1)

    def setIsVehiclesCompareEnabled(self, value):
        self._setBool(1, value)

    def getVehicleCompareTooltipId(self):
        return self._getString(2)

    def setVehicleCompareTooltipId(self, value):
        self._setString(2, value)

    def getSelectedProductId(self):
        return self._getNumber(3)

    def setSelectedProductId(self, value):
        self._setNumber(3, value)

    def getCurrentRank(self):
        return Rank(self._getNumber(4))

    def setCurrentRank(self, value):
        self._setNumber(4, value.value)

    def getMaxAchievedRank(self):
        return Rank(self._getNumber(5))

    def setMaxAchievedRank(self, value):
        self._setNumber(5, value.value)

    def getRankDiscounts(self):
        return self._getArray(6)

    def setRankDiscounts(self, value):
        self._setArray(6, value)

    @staticmethod
    def getRankDiscountsType():
        return RankDiscountModel

    def getProducts(self):
        return self._getArray(7)

    def setProducts(self, value):
        self._setArray(7, value)

    @staticmethod
    def getProductsType():
        return BaseProductModel

    def _initialize(self):
        super(ShopModel, self)._initialize()
        self._addNumberProperty('shopState')
        self._addBoolProperty('isVehiclesCompareEnabled', True)
        self._addStringProperty('vehicleCompareTooltipId', '')
        self._addNumberProperty('selectedProductId', 0)
        self._addNumberProperty('currentRank')
        self._addNumberProperty('maxAchievedRank')
        self._addArrayProperty('rankDiscounts', Array())
        self._addArrayProperty('products', Array())
        self.onProductSeen = self._addCommand('onProductSeen')
        self.onProductSelect = self._addCommand('onProductSelect')
        self.onProductPurchase = self._addCommand('onProductPurchase')
        self.onProductRestore = self._addCommand('onProductRestore')
        self.onGoToHangar = self._addCommand('onGoToHangar')
        self.onGoToPreview = self._addCommand('onGoToPreview')
        self.onGoToCustomization = self._addCommand('onGoToCustomization')
        self.onAddToVehicleCompare = self._addCommand('onAddToVehicleCompare')
        self.onMouseOver3dScene = self._addCommand('onMouseOver3dScene')
        self.onMoveSpace = self._addCommand('onMoveSpace')
