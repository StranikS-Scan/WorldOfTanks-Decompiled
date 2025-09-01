# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/dialogs/purchase_dialog_model.py
from enum import IntEnum
from frameworks.wulf import Array, ViewModel
from comp7.gui.impl.gen.view_models.views.lobby.base_product_model import BaseProductModel

class PageState(IntEnum):
    CONFIRMATION = 0
    FLYBY = 1
    CONGRATULATION = 2
    ERROR = 3


class PurchaseDialogModel(ViewModel):
    __slots__ = ('onClose', 'onConfirm', 'onMouseOver3dScene', 'onMoveSpace')

    def __init__(self, properties=4, commands=4):
        super(PurchaseDialogModel, self).__init__(properties=properties, commands=commands)

    def getPageState(self):
        return PageState(self._getNumber(0))

    def setPageState(self, value):
        self._setNumber(0, value.value)

    def getProduct(self):
        return self._getArray(1)

    def setProduct(self, value):
        self._setArray(1, value)

    @staticmethod
    def getProductType():
        return BaseProductModel

    def getHasSuitableVehicle(self):
        return self._getBool(2)

    def setHasSuitableVehicle(self, value):
        self._setBool(2, value)

    def getIsPurchaseProcessing(self):
        return self._getBool(3)

    def setIsPurchaseProcessing(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(PurchaseDialogModel, self)._initialize()
        self._addNumberProperty('pageState', PageState.CONFIRMATION.value)
        self._addArrayProperty('product', Array())
        self._addBoolProperty('hasSuitableVehicle', False)
        self._addBoolProperty('isPurchaseProcessing', False)
        self.onClose = self._addCommand('onClose')
        self.onConfirm = self._addCommand('onConfirm')
        self.onMouseOver3dScene = self._addCommand('onMouseOver3dScene')
        self.onMoveSpace = self._addCommand('onMoveSpace')
