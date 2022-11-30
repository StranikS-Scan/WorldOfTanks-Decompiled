# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/dialogs/glade/customization_buy_dialog_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class CustomizationBuyDialogModel(ViewModel):
    __slots__ = ('onAccept', 'onCancel')

    def __init__(self, properties=8, commands=2):
        super(CustomizationBuyDialogModel, self).__init__(properties=properties, commands=commands)

    def getPrice(self):
        return self._getNumber(0)

    def setPrice(self, value):
        self._setNumber(0, value)

    def getTotalCurrency(self):
        return self._getNumber(1)

    def setTotalCurrency(self, value):
        self._setNumber(1, value)

    def getToyName(self):
        return self._getResource(2)

    def setToyName(self, value):
        self._setResource(2, value)

    def getToyIcon(self):
        return self._getResource(3)

    def setToyIcon(self, value):
        self._setResource(3, value)

    def getCanBuy(self):
        return self._getBool(4)

    def setCanBuy(self, value):
        self._setBool(4, value)

    def getIsError(self):
        return self._getBool(5)

    def setIsError(self, value):
        self._setBool(5, value)

    def getEnoughMoney(self):
        return self._getBool(6)

    def setEnoughMoney(self, value):
        self._setBool(6, value)

    def getEventTimeLeft(self):
        return self._getNumber(7)

    def setEventTimeLeft(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(CustomizationBuyDialogModel, self)._initialize()
        self._addNumberProperty('price', 0)
        self._addNumberProperty('totalCurrency', 0)
        self._addResourceProperty('toyName', R.invalid())
        self._addResourceProperty('toyIcon', R.invalid())
        self._addBoolProperty('canBuy', False)
        self._addBoolProperty('isError', False)
        self._addBoolProperty('enoughMoney', False)
        self._addNumberProperty('eventTimeLeft', 0)
        self.onAccept = self._addCommand('onAccept')
        self.onCancel = self._addCommand('onCancel')
