# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_cart/cart_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.customization.customization_cart.cart_purchase_model import CartPurchaseModel
from gui.impl.gen.view_models.views.lobby.customization.customization_cart.cart_rent_model import CartRentModel
from gui.impl.gen.view_models.views.lobby.customization.customization_cart.cart_seasons_model import CartSeasonsModel
from gui.impl.gen.view_models.views.lobby.customization.customization_cart.cart_style_model import CartStyleModel
from gui.impl.gen.view_models.views.lobby.customization.customization_cart.cart_tutorial_model import CartTutorialModel

class CartModel(ViewModel):
    __slots__ = ('onCloseAction',)

    def __init__(self, properties=7, commands=1):
        super(CartModel, self).__init__(properties=properties, commands=commands)

    @property
    def seasons(self):
        return self._getViewModel(0)

    @staticmethod
    def getSeasonsType():
        return CartSeasonsModel

    @property
    def style(self):
        return self._getViewModel(1)

    @staticmethod
    def getStyleType():
        return CartStyleModel

    @property
    def purchase(self):
        return self._getViewModel(2)

    @staticmethod
    def getPurchaseType():
        return CartPurchaseModel

    @property
    def rent(self):
        return self._getViewModel(3)

    @staticmethod
    def getRentType():
        return CartRentModel

    @property
    def tutorial(self):
        return self._getViewModel(4)

    @staticmethod
    def getTutorialType():
        return CartTutorialModel

    def getIsAnySelected(self):
        return self._getBool(5)

    def setIsAnySelected(self, value):
        self._setBool(5, value)

    def getIsRendererPipelineDeferred(self):
        return self._getBool(6)

    def setIsRendererPipelineDeferred(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(CartModel, self)._initialize()
        self._addViewModelProperty('seasons', CartSeasonsModel())
        self._addViewModelProperty('style', CartStyleModel())
        self._addViewModelProperty('purchase', CartPurchaseModel())
        self._addViewModelProperty('rent', CartRentModel())
        self._addViewModelProperty('tutorial', CartTutorialModel())
        self._addBoolProperty('isAnySelected', False)
        self._addBoolProperty('isRendererPipelineDeferred', False)
        self.onCloseAction = self._addCommand('onCloseAction')
