# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/apply_convert_currency_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class ApplyConvertCurrencyModel(FullScreenDialogWindowModel):
    __slots__ = ('onChangeGold', 'onChangeCredits')

    def __init__(self, properties=19, commands=5):
        super(ApplyConvertCurrencyModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(11)

    def getUserTotalGold(self):
        return self._getNumber(12)

    def setUserTotalGold(self, value):
        self._setNumber(12, value)

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

    def getConvertGold(self):
        return self._getNumber(16)

    def setConvertGold(self, value):
        self._setNumber(16, value)

    def getConvertCredits(self):
        return self._getNumber(17)

    def setConvertCredits(self, value):
        self._setNumber(17, value)

    def getNotEnoughCredits(self):
        return self._getNumber(18)

    def setNotEnoughCredits(self, value):
        self._setNumber(18, value)

    def _initialize(self):
        super(ApplyConvertCurrencyModel, self)._initialize()
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addNumberProperty('userTotalGold', 0)
        self._addNumberProperty('goldToCreditsExchangeRate', 0)
        self._addBoolProperty('goldToCreditsIsDiscount', False)
        self._addNumberProperty('goldToCreditsDiscountValue', 0)
        self._addNumberProperty('convertGold', 0)
        self._addNumberProperty('convertCredits', 0)
        self._addNumberProperty('notEnoughCredits', 0)
        self.onChangeGold = self._addCommand('onChangeGold')
        self.onChangeCredits = self._addCommand('onChangeCredits')
