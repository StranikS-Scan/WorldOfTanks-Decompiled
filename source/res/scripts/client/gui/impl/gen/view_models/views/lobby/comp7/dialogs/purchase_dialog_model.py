# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/dialogs/purchase_dialog_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_item_model import PriceItemModel
from gui.impl.gen.view_models.views.lobby.comp7.base_product_model import BaseProductModel

class PageState(IntEnum):
    CONFIRMATION = 0
    FLYBY = 1
    CONGRATULATION = 2
    ERROR = 3


class PurchaseDialogModel(ViewModel):
    __slots__ = ('onClose', 'onConfirm', 'onMouseOver3dScene', 'onMoveSpace')

    def __init__(self, properties=6, commands=4):
        super(PurchaseDialogModel, self).__init__(properties=properties, commands=commands)

    def getPageState(self):
        return PageState(self._getNumber(0))

    def setPageState(self, value):
        self._setNumber(0, value.value)

    def getBalance(self):
        return self._getArray(1)

    def setBalance(self, value):
        self._setArray(1, value)

    @staticmethod
    def getBalanceType():
        return PriceItemModel

    def getIsWGMAvailable(self):
        return self._getBool(2)

    def setIsWGMAvailable(self, value):
        self._setBool(2, value)

    def getProduct(self):
        return self._getArray(3)

    def setProduct(self, value):
        self._setArray(3, value)

    @staticmethod
    def getProductType():
        return BaseProductModel

    def getHasSuitableVehicle(self):
        return self._getBool(4)

    def setHasSuitableVehicle(self, value):
        self._setBool(4, value)

    def getIsPurchaseProcessing(self):
        return self._getBool(5)

    def setIsPurchaseProcessing(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(PurchaseDialogModel, self)._initialize()
        self._addNumberProperty('pageState', PageState.CONFIRMATION.value)
        self._addArrayProperty('balance', Array())
        self._addBoolProperty('isWGMAvailable', False)
        self._addArrayProperty('product', Array())
        self._addBoolProperty('hasSuitableVehicle', False)
        self._addBoolProperty('isPurchaseProcessing', False)
        self.onClose = self._addCommand('onClose')
        self.onConfirm = self._addCommand('onConfirm')
        self.onMouseOver3dScene = self._addCommand('onMouseOver3dScene')
        self.onMoveSpace = self._addCommand('onMoveSpace')
