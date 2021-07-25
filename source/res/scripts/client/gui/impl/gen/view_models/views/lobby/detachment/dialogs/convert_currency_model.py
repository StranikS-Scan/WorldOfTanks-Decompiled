# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/convert_currency_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class ConvertCurrencyModel(FullScreenDialogWindowModel):
    __slots__ = ('onAccept',)
    VEHICLE = 'vehicle'
    BOOKS = 'books'
    DETACHMENT = 'detachment'
    TANKMAN = 'tankman'
    MATRIX_EDIT = 'matrixEdit'

    def __init__(self, properties=18, commands=4):
        super(ConvertCurrencyModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getResource(11)

    def setIcon(self, value):
        self._setResource(11, value)

    def getType(self):
        return self._getString(12)

    def setType(self, value):
        self._setString(12, value)

    def getGoldToCreditsExchangeRate(self):
        return self._getNumber(13)

    def setGoldToCreditsExchangeRate(self, value):
        self._setNumber(13, value)

    def getGoldToCreditsIsDiscount(self):
        return self._getBool(14)

    def setGoldToCreditsIsDiscount(self, value):
        self._setBool(14, value)

    def getGoldToCreditsDiscountValue(self):
        return self._getNumber(15)

    def setGoldToCreditsDiscountValue(self, value):
        self._setNumber(15, value)

    def getNotEnoughCredits(self):
        return self._getNumber(16)

    def setNotEnoughCredits(self, value):
        self._setNumber(16, value)

    def getExtraData(self):
        return self._getArray(17)

    def setExtraData(self, value):
        self._setArray(17, value)

    def _initialize(self):
        super(ConvertCurrencyModel, self)._initialize()
        self._addResourceProperty('icon', R.invalid())
        self._addStringProperty('type', '')
        self._addNumberProperty('goldToCreditsExchangeRate', 0)
        self._addBoolProperty('goldToCreditsIsDiscount', False)
        self._addNumberProperty('goldToCreditsDiscountValue', 0)
        self._addNumberProperty('notEnoughCredits', 0)
        self._addArrayProperty('extraData', Array())
        self.onAccept = self._addCommand('onAccept')
