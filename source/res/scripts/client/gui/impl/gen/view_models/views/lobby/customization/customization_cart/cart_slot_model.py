# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_cart/cart_slot_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_compound_price_model import UserCompoundPriceModel

class CartSlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=18, commands=0):
        super(CartSlotModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    def getId(self):
        return self._getNumber(1)

    def setId(self, value):
        self._setNumber(1, value)

    def getTypeId(self):
        return self._getNumber(2)

    def setTypeId(self, value):
        self._setNumber(2, value)

    def getLocked(self):
        return self._getBool(3)

    def setLocked(self, value):
        self._setBool(3, value)

    def getSelected(self):
        return self._getBool(4)

    def setSelected(self, value):
        self._setBool(4, value)

    def getIsFromStorage(self):
        return self._getBool(5)

    def setIsFromStorage(self, value):
        self._setBool(5, value)

    def getIcon(self):
        return self._getString(6)

    def setIcon(self, value):
        self._setString(6, value)

    def getQuantity(self):
        return self._getNumber(7)

    def setQuantity(self, value):
        self._setNumber(7, value)

    def getTooltipId(self):
        return self._getString(8)

    def setTooltipId(self, value):
        self._setString(8, value)

    def getIsWide(self):
        return self._getBool(9)

    def setIsWide(self, value):
        self._setBool(9, value)

    def getIsDim(self):
        return self._getBool(10)

    def setIsDim(self, value):
        self._setBool(10, value)

    def getFormFactor(self):
        return self._getString(11)

    def setFormFactor(self, value):
        self._setString(11, value)

    def getIsHistorical(self):
        return self._getBool(12)

    def setIsHistorical(self, value):
        self._setBool(12, value)

    def getIsSpecial(self):
        return self._getBool(13)

    def setIsSpecial(self, value):
        self._setBool(13, value)

    def getShowUnsupportedAlert(self):
        return self._getBool(14)

    def setShowUnsupportedAlert(self, value):
        self._setBool(14, value)

    def getProgressionLevel(self):
        return self._getNumber(15)

    def setProgressionLevel(self, value):
        self._setNumber(15, value)

    def getIsEdited(self):
        return self._getBool(16)

    def setIsEdited(self, value):
        self._setBool(16, value)

    def getIsStyle(self):
        return self._getBool(17)

    def setIsStyle(self, value):
        self._setBool(17, value)

    def _initialize(self):
        super(CartSlotModel, self)._initialize()
        self._addViewModelProperty('price', UserCompoundPriceModel())
        self._addNumberProperty('id', 0)
        self._addNumberProperty('typeId', 0)
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
        self._addNumberProperty('progressionLevel', 0)
        self._addBoolProperty('isEdited', False)
        self._addBoolProperty('isStyle', False)
