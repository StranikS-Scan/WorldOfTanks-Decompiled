# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_shop_view_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_model import PriceModel
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_shop_item import ArmoryYardShopItem

class BackButtonState(IntEnum):
    ARMORY = 0
    INGAMESHOP = 1


class ArmoryYardShopViewModel(ViewModel):
    __slots__ = ('onBack', 'onClose', 'onCloseIntro', 'onShowIntro', 'onBuyProduct')

    def __init__(self, properties=5, commands=5):
        super(ArmoryYardShopViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def tokenPrice(self):
        return self._getViewModel(0)

    @staticmethod
    def getTokenPriceType():
        return PriceModel

    def getIsIntroVisible(self):
        return self._getBool(1)

    def setIsIntroVisible(self, value):
        self._setBool(1, value)

    def getCurrency(self):
        return self._getNumber(2)

    def setCurrency(self, value):
        self._setNumber(2, value)

    def getBackButtonState(self):
        return BackButtonState(self._getNumber(3))

    def setBackButtonState(self, value):
        self._setNumber(3, value.value)

    def getItems(self):
        return self._getArray(4)

    def setItems(self, value):
        self._setArray(4, value)

    @staticmethod
    def getItemsType():
        return ArmoryYardShopItem

    def _initialize(self):
        super(ArmoryYardShopViewModel, self)._initialize()
        self._addViewModelProperty('tokenPrice', PriceModel())
        self._addBoolProperty('isIntroVisible', False)
        self._addNumberProperty('currency', 0)
        self._addNumberProperty('backButtonState')
        self._addArrayProperty('items', Array())
        self.onBack = self._addCommand('onBack')
        self.onClose = self._addCommand('onClose')
        self.onCloseIntro = self._addCommand('onCloseIntro')
        self.onShowIntro = self._addCommand('onShowIntro')
        self.onBuyProduct = self._addCommand('onBuyProduct')
