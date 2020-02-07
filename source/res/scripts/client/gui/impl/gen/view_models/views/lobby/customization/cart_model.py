# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/cart_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.customization.cart_purchase_model import CartPurchaseModel
from gui.impl.gen.view_models.views.lobby.customization.cart_rent_model import CartRentModel
from gui.impl.gen.view_models.views.lobby.customization.cart_seasons_model import CartSeasonsModel
from gui.impl.gen.view_models.views.lobby.customization.cart_style_model import CartStyleModel
from gui.impl.gen.view_models.views.lobby.customization.cart_tutorial_model import CartTutorialModel

class CartModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(CartModel, self).__init__(properties=properties, commands=commands)

    @property
    def seasons(self):
        return self._getViewModel(0)

    @property
    def style(self):
        return self._getViewModel(1)

    @property
    def purchase(self):
        return self._getViewModel(2)

    @property
    def rent(self):
        return self._getViewModel(3)

    @property
    def tutorial(self):
        return self._getViewModel(4)

    def getIsAnySelected(self):
        return self._getBool(5)

    def setIsAnySelected(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(CartModel, self)._initialize()
        self._addViewModelProperty('seasons', CartSeasonsModel())
        self._addViewModelProperty('style', CartStyleModel())
        self._addViewModelProperty('purchase', CartPurchaseModel())
        self._addViewModelProperty('rent', CartRentModel())
        self._addViewModelProperty('tutorial', CartTutorialModel())
        self._addBoolProperty('isAnySelected', False)
