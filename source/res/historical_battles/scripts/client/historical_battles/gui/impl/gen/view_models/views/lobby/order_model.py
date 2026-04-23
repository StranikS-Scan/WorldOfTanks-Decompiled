# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/order_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class OrderType(Enum):
    SMALL = 'x2'
    MEDIUM = 'x3'
    BIG = 'x5'


class OrderModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
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

    def _initialize(self):
        super(OrderModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addNumberProperty('count', 0)
        self._addStringProperty('type')
