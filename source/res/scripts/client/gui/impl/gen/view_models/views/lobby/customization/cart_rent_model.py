# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/cart_rent_model.py
from frameworks.wulf import ViewModel

class CartRentModel(ViewModel):
    __slots__ = ('onSelectAutoRent',)

    def __init__(self, properties=4, commands=1):
        super(CartRentModel, self).__init__(properties=properties, commands=commands)

    def getIsRentable(self):
        return self._getBool(0)

    def setIsRentable(self, value):
        self._setBool(0, value)

    def getRentCount(self):
        return self._getNumber(1)

    def setRentCount(self, value):
        self._setNumber(1, value)

    def getHasAutoRent(self):
        return self._getBool(2)

    def setHasAutoRent(self, value):
        self._setBool(2, value)

    def getIsAutoRentSelected(self):
        return self._getBool(3)

    def setIsAutoRentSelected(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(CartRentModel, self)._initialize()
        self._addBoolProperty('isRentable', False)
        self._addNumberProperty('rentCount', 0)
        self._addBoolProperty('hasAutoRent', False)
        self._addBoolProperty('isAutoRentSelected', False)
        self.onSelectAutoRent = self._addCommand('onSelectAutoRent')
