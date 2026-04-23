# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_bill_data_model.py
from gui.impl.gen.view_models.views.lobby.customization.customization_bill_base_model import CustomizationBillBaseModel

class CustomizationBillDataModel(CustomizationBillBaseModel):
    __slots__ = ('onAutoRentHintClose', 'onAutoRentChange', 'onCancelChanges', 'onClearBasket', 'onShowBuyWindow')

    def __init__(self, properties=15, commands=5):
        super(CustomizationBillDataModel, self).__init__(properties=properties, commands=commands)

    def getCancelButtonEnabled(self):
        return self._getBool(10)

    def setCancelButtonEnabled(self, value):
        self._setBool(10, value)

    def getClearButtonEnabled(self):
        return self._getBool(11)

    def setClearButtonEnabled(self, value):
        self._setBool(11, value)

    def getIsAutoRentSelected(self):
        return self._getBool(12)

    def setIsAutoRentSelected(self, value):
        self._setBool(12, value)

    def getShowAutoRentHint(self):
        return self._getBool(13)

    def setShowAutoRentHint(self, value):
        self._setBool(13, value)

    def getIsLockedItem(self):
        return self._getBool(14)

    def setIsLockedItem(self, value):
        self._setBool(14, value)

    def _initialize(self):
        super(CustomizationBillDataModel, self)._initialize()
        self._addBoolProperty('cancelButtonEnabled', False)
        self._addBoolProperty('clearButtonEnabled', False)
        self._addBoolProperty('isAutoRentSelected', False)
        self._addBoolProperty('showAutoRentHint', False)
        self._addBoolProperty('isLockedItem', False)
        self.onAutoRentHintClose = self._addCommand('onAutoRentHintClose')
        self.onAutoRentChange = self._addCommand('onAutoRentChange')
        self.onCancelChanges = self._addCommand('onCancelChanges')
        self.onClearBasket = self._addCommand('onClearBasket')
        self.onShowBuyWindow = self._addCommand('onShowBuyWindow')
