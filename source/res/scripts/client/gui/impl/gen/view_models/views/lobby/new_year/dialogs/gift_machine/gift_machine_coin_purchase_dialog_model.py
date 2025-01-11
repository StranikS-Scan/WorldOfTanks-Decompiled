# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/dialogs/gift_machine/gift_machine_coin_purchase_dialog_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resource_model import NyResourceModel

class DialogState(Enum):
    DEFAULT = 'default'
    PURCHASING = 'purchasing'
    ERROR = 'error'


class GiftMachineCoinPurchaseDialogModel(ViewModel):
    __slots__ = ('onAccept', 'onCancel')

    def __init__(self, properties=5, commands=2):
        super(GiftMachineCoinPurchaseDialogModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return NyResourceModel

    def getResources(self):
        return self._getArray(1)

    def setResources(self, value):
        self._setArray(1, value)

    @staticmethod
    def getResourcesType():
        return NyResourceModel

    def getDialogState(self):
        return DialogState(self._getString(2))

    def setDialogState(self, value):
        self._setString(2, value.value)

    def getIsWalletAvailable(self):
        return self._getBool(3)

    def setIsWalletAvailable(self, value):
        self._setBool(3, value)

    def getTokenAmount(self):
        return self._getNumber(4)

    def setTokenAmount(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(GiftMachineCoinPurchaseDialogModel, self)._initialize()
        self._addViewModelProperty('price', NyResourceModel())
        self._addArrayProperty('resources', Array())
        self._addStringProperty('dialogState')
        self._addBoolProperty('isWalletAvailable', True)
        self._addNumberProperty('tokenAmount', 0)
        self.onAccept = self._addCommand('onAccept')
        self.onCancel = self._addCommand('onCancel')
