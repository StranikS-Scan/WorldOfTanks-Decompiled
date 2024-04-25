# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/order_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class OrderType(Enum):
    SMALL = 'x5'
    MEDIUM = 'x10'
    BIG = 'x15'


class OrderModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(OrderModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getCount(self):
        return self._getNumber(1)

    def setCount(self, value):
        self._setNumber(1, value)

    def getType(self):
        return OrderType(self._getString(2))

    def setType(self, value):
        self._setString(2, value.value)

    def getIsActive(self):
        return self._getBool(3)

    def setIsActive(self, value):
        self._setBool(3, value)

    def getIsIconAnimated(self):
        return self._getBool(4)

    def setIsIconAnimated(self, value):
        self._setBool(4, value)

    def getIsBorderAnimated(self):
        return self._getBool(5)

    def setIsBorderAnimated(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(OrderModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addNumberProperty('count', 0)
        self._addStringProperty('type')
        self._addBoolProperty('isActive', False)
        self._addBoolProperty('isIconAnimated', False)
        self._addBoolProperty('isBorderAnimated', False)
