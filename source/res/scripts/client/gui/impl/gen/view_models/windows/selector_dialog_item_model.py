# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/selector_dialog_item_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class SelectorDialogItemModel(ViewModel):
    __slots__ = ()
    DEMOUNT_KIT = 'demountKit'
    WAIT = 'wait'
    GOLD = 'gold'
    CREDITS = 'credits'
    BLANK = 'blank'
    HANGAR = 'hangar'
    AMMO = 'ammo'
    NOTHING = ''
    DISABLED = 'disabled'
    WARNING = 'warning'
    ALARM = 'alarm'

    def __init__(self, properties=11, commands=0):
        super(SelectorDialogItemModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getTitle(self):
        return self._getResource(1)

    def setTitle(self, value):
        self._setResource(1, value)

    def getItemPrice(self):
        return self._getNumber(2)

    def setItemPrice(self, value):
        self._setNumber(2, value)

    def getCurrencyType(self):
        return self._getString(3)

    def setCurrencyType(self, value):
        self._setString(3, value)

    def getStorageCount(self):
        return self._getNumber(4)

    def setStorageCount(self, value):
        self._setNumber(4, value)

    def getStatus(self):
        return self._getString(5)

    def setStatus(self, value):
        self._setString(5, value)

    def getIsItemEnough(self):
        return self._getBool(6)

    def setIsItemEnough(self, value):
        self._setBool(6, value)

    def getIsDiscount(self):
        return self._getBool(7)

    def setIsDiscount(self, value):
        self._setBool(7, value)

    def getDiscountValue(self):
        return self._getNumber(8)

    def setDiscountValue(self, value):
        self._setNumber(8, value)

    def getIsSelected(self):
        return self._getBool(9)

    def setIsSelected(self, value):
        self._setBool(9, value)

    def getTooltipId(self):
        return self._getString(10)

    def setTooltipId(self, value):
        self._setString(10, value)

    def _initialize(self):
        super(SelectorDialogItemModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addResourceProperty('title', R.invalid())
        self._addNumberProperty('itemPrice', 0)
        self._addStringProperty('currencyType', '')
        self._addNumberProperty('storageCount', 0)
        self._addStringProperty('status', '')
        self._addBoolProperty('isItemEnough', True)
        self._addBoolProperty('isDiscount', False)
        self._addNumberProperty('discountValue', 0)
        self._addBoolProperty('isSelected', False)
        self._addStringProperty('tooltipId', '')
