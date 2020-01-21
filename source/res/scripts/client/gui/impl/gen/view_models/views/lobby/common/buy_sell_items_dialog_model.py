# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/buy_sell_items_dialog_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class BuySellItemsDialogModel(FullScreenDialogWindowModel):
    __slots__ = ()
    BATTLE_BOOSTER_CREW_REPLACE = 'battleBoosterReplace'
    BATTLE_BOOSTER = 'battleBooster'

    def __init__(self, properties=23, commands=2):
        super(BuySellItemsDialogModel, self).__init__(properties=properties, commands=commands)

    def getBackgroundImg(self):
        return self._getResource(10)

    def setBackgroundImg(self, value):
        self._setResource(10, value)

    def getDescription(self):
        return self._getResource(11)

    def setDescription(self, value):
        self._setResource(11, value)

    def getUpperDescription(self):
        return self._getResource(12)

    def setUpperDescription(self, value):
        self._setResource(12, value)

    def getLowerDescription(self):
        return self._getResource(13)

    def setLowerDescription(self, value):
        self._setResource(13, value)

    def getIsAlert(self):
        return self._getBool(14)

    def setIsAlert(self, value):
        self._setBool(14, value)

    def getCurrencyType(self):
        return self._getString(15)

    def setCurrencyType(self, value):
        self._setString(15, value)

    def getItemPrice(self):
        return self._getNumber(16)

    def setItemPrice(self, value):
        self._setNumber(16, value)

    def getItemCount(self):
        return self._getNumber(17)

    def setItemCount(self, value):
        self._setNumber(17, value)

    def getItemMaxCount(self):
        return self._getNumber(18)

    def setItemMaxCount(self, value):
        self._setNumber(18, value)

    def getItemMinCount(self):
        return self._getNumber(19)

    def setItemMinCount(self, value):
        self._setNumber(19, value)

    def getItemTotalPrice(self):
        return self._getNumber(20)

    def setItemTotalPrice(self, value):
        self._setNumber(20, value)

    def getTooltipMsg(self):
        return self._getString(21)

    def setTooltipMsg(self, value):
        self._setString(21, value)

    def getItemType(self):
        return self._getString(22)

    def setItemType(self, value):
        self._setString(22, value)

    def _initialize(self):
        super(BuySellItemsDialogModel, self)._initialize()
        self._addResourceProperty('backgroundImg', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addResourceProperty('upperDescription', R.invalid())
        self._addResourceProperty('lowerDescription', R.invalid())
        self._addBoolProperty('isAlert', False)
        self._addStringProperty('currencyType', '')
        self._addNumberProperty('itemPrice', 0)
        self._addNumberProperty('itemCount', 1)
        self._addNumberProperty('itemMaxCount', 1)
        self._addNumberProperty('itemMinCount', 1)
        self._addNumberProperty('itemTotalPrice', 0)
        self._addStringProperty('tooltipMsg', '')
        self._addStringProperty('itemType', '')
