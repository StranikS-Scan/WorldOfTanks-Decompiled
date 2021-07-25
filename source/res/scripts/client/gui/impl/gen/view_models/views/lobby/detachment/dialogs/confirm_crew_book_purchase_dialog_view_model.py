# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/confirm_crew_book_purchase_dialog_view_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.price_model import PriceModel
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class ConfirmCrewBookPurchaseDialogViewModel(FullScreenDialogWindowModel):
    __slots__ = ('onStepperChange',)

    def __init__(self, properties=17, commands=4):
        super(ConfirmCrewBookPurchaseDialogViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def priceModel(self):
        return self._getViewModel(11)

    def getNation(self):
        return self._getString(12)

    def setNation(self, value):
        self._setString(12, value)

    def getCrewBookType(self):
        return self._getString(13)

    def setCrewBookType(self, value):
        self._setString(13, value)

    def getAmountXP(self):
        return self._getNumber(14)

    def setAmountXP(self, value):
        self._setNumber(14, value)

    def getMaxValue(self):
        return self._getNumber(15)

    def setMaxValue(self, value):
        self._setNumber(15, value)

    def getSelectedValue(self):
        return self._getNumber(16)

    def setSelectedValue(self, value):
        self._setNumber(16, value)

    def _initialize(self):
        super(ConfirmCrewBookPurchaseDialogViewModel, self)._initialize()
        self._addViewModelProperty('priceModel', PriceModel())
        self._addStringProperty('nation', '')
        self._addStringProperty('crewBookType', '')
        self._addNumberProperty('amountXP', 0)
        self._addNumberProperty('maxValue', 1)
        self._addNumberProperty('selectedValue', 1)
        self.onStepperChange = self._addCommand('onStepperChange')
