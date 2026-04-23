# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/historical_battles/dialogs/content/order_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class OrderType(Enum):
    SMALL = 'x5'
    MEDIUM = 'x10'
    BIG = 'x15'


class OrderModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(OrderModel, self).__init__(properties=properties, commands=commands)

    def getCount(self):
        return self._getNumber(0)

    def setCount(self, value):
        self._setNumber(0, value)

    def getType(self):
        return OrderType(self._getString(1))

    def setType(self, value):
        self._setString(1, value.value)

    def _initialize(self):
        super(OrderModel, self)._initialize()
        self._addNumberProperty('count', 0)
        self._addStringProperty('type')
