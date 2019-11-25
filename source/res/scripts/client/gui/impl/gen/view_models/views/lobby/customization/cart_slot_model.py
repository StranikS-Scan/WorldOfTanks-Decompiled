# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/cart_slot_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_compound_price_model import UserCompoundPriceModel

class CartSlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(CartSlotModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    def getId(self):
        return self._getNumber(1)

    def setId(self, value):
        self._setNumber(1, value)

    def getLocked(self):
        return self._getBool(2)

    def setLocked(self, value):
        self._setBool(2, value)

    def getSelected(self):
        return self._getBool(3)

    def setSelected(self, value):
        self._setBool(3, value)

    def getIsFromStorage(self):
        return self._getBool(4)

    def setIsFromStorage(self, value):
        self._setBool(4, value)

    def getIcon(self):
        return self._getString(5)

    def setIcon(self, value):
        self._setString(5, value)

    def getQuantity(self):
        return self._getNumber(6)

    def setQuantity(self, value):
        self._setNumber(6, value)

    def getTooltipId(self):
        return self._getString(7)

    def setTooltipId(self, value):
        self._setString(7, value)

    def getIsWide(self):
        return self._getBool(8)

    def setIsWide(self, value):
        self._setBool(8, value)

    def getIsDim(self):
        return self._getBool(9)

    def setIsDim(self, value):
        self._setBool(9, value)

    def getFormFactor(self):
        return self._getString(10)

    def setFormFactor(self, value):
        self._setString(10, value)

    def getIsHistorical(self):
        return self._getBool(11)

    def setIsHistorical(self, value):
        self._setBool(11, value)

    def getIsSpecial(self):
        return self._getBool(12)

    def setIsSpecial(self, value):
        self._setBool(12, value)

    def getShowUnsupportedAlert(self):
        return self._getBool(13)

    def setShowUnsupportedAlert(self, value):
        self._setBool(13, value)

    def _initialize(self):
        super(CartSlotModel, self)._initialize()
        self._addViewModelProperty('price', UserCompoundPriceModel())
        self._addNumberProperty('id', 0)
        self._addBoolProperty('locked', False)
        self._addBoolProperty('selected', True)
        self._addBoolProperty('isFromStorage', False)
        self._addStringProperty('icon', '')
        self._addNumberProperty('quantity', 0)
        self._addStringProperty('tooltipId', '')
        self._addBoolProperty('isWide', False)
        self._addBoolProperty('isDim', False)
        self._addStringProperty('formFactor', '')
        self._addBoolProperty('isHistorical', False)
        self._addBoolProperty('isSpecial', False)
        self._addBoolProperty('showUnsupportedAlert', False)
