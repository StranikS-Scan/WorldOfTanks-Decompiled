# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/cart_slot_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_model import PriceModel

class CartSlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=24, commands=0):
        super(CartSlotModel, self).__init__(properties=properties, commands=commands)

    @property
    def buyPrice(self):
        return self._getViewModel(0)

    @staticmethod
    def getBuyPriceType():
        return PriceModel

    def getItemID(self):
        return self._getNumber(1)

    def setItemID(self, value):
        self._setNumber(1, value)

    def getIntCD(self):
        return self._getNumber(2)

    def setIntCD(self, value):
        self._setNumber(2, value)

    def getExtraName(self):
        return self._getString(3)

    def setExtraName(self, value):
        self._setString(3, value)

    def getIsMainType(self):
        return self._getBool(4)

    def setIsMainType(self, value):
        self._setBool(4, value)

    def getIsWithSerialNumber(self):
        return self._getBool(5)

    def setIsWithSerialNumber(self, value):
        self._setBool(5, value)

    def getIsRental(self):
        return self._getBool(6)

    def setIsRental(self, value):
        self._setBool(6, value)

    def getRentalInfoText(self):
        return self._getString(7)

    def setRentalInfoText(self, value):
        self._setString(7, value)

    def getAutoRentEnabled(self):
        return self._getBool(8)

    def setAutoRentEnabled(self, value):
        self._setBool(8, value)

    def getTypeId(self):
        return self._getNumber(9)

    def setTypeId(self, value):
        self._setNumber(9, value)

    def getIsSelected(self):
        return self._getBool(10)

    def setIsSelected(self, value):
        self._setBool(10, value)

    def getIsDisabled(self):
        return self._getBool(11)

    def setIsDisabled(self, value):
        self._setBool(11, value)

    def getIsFromStorage(self):
        return self._getBool(12)

    def setIsFromStorage(self, value):
        self._setBool(12, value)

    def getIcon(self):
        return self._getString(13)

    def setIcon(self, value):
        self._setString(13, value)

    def getQuantity(self):
        return self._getNumber(14)

    def setQuantity(self, value):
        self._setNumber(14, value)

    def getTooltip(self):
        return self._getString(15)

    def setTooltip(self, value):
        self._setString(15, value)

    def getIsWide(self):
        return self._getBool(16)

    def setIsWide(self, value):
        self._setBool(16, value)

    def getIsDim(self):
        return self._getBool(17)

    def setIsDim(self, value):
        self._setBool(17, value)

    def getCustomizationDisplayType(self):
        return self._getNumber(18)

    def setCustomizationDisplayType(self, value):
        self._setNumber(18, value)

    def getIsSpecial(self):
        return self._getBool(19)

    def setIsSpecial(self, value):
        self._setBool(19, value)

    def getShowAlert(self):
        return self._getBool(20)

    def setShowAlert(self, value):
        self._setBool(20, value)

    def getProgressionLevel(self):
        return self._getNumber(21)

    def setProgressionLevel(self, value):
        self._setNumber(21, value)

    def getIsProgressionRewindEnabled(self):
        return self._getBool(22)

    def setIsProgressionRewindEnabled(self, value):
        self._setBool(22, value)

    def getIsEdited(self):
        return self._getBool(23)

    def setIsEdited(self, value):
        self._setBool(23, value)

    def _initialize(self):
        super(CartSlotModel, self)._initialize()
        self._addViewModelProperty('buyPrice', PriceModel())
        self._addNumberProperty('itemID', 0)
        self._addNumberProperty('intCD', 0)
        self._addStringProperty('extraName', '')
        self._addBoolProperty('isMainType', False)
        self._addBoolProperty('isWithSerialNumber', False)
        self._addBoolProperty('isRental', False)
        self._addStringProperty('rentalInfoText', '')
        self._addBoolProperty('autoRentEnabled', False)
        self._addNumberProperty('typeId', 0)
        self._addBoolProperty('isSelected', True)
        self._addBoolProperty('isDisabled', False)
        self._addBoolProperty('isFromStorage', False)
        self._addStringProperty('icon', '')
        self._addNumberProperty('quantity', 0)
        self._addStringProperty('tooltip', '')
        self._addBoolProperty('isWide', False)
        self._addBoolProperty('isDim', False)
        self._addNumberProperty('customizationDisplayType', 1)
        self._addBoolProperty('isSpecial', False)
        self._addBoolProperty('showAlert', False)
        self._addNumberProperty('progressionLevel', -1)
        self._addBoolProperty('isProgressionRewindEnabled', False)
        self._addBoolProperty('isEdited', False)
