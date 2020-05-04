# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/order_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class OrderModel(ViewModel):
    __slots__ = ()
    TIMER = 'timer'
    BUY = 'buy'
    EXCHANGE = 'exchange'

    def __init__(self, properties=10, commands=0):
        super(OrderModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getCount(self):
        return self._getNumber(1)

    def setCount(self, value):
        self._setNumber(1, value)

    def getTimer(self):
        return self._getNumber(2)

    def setTimer(self, value):
        self._setNumber(2, value)

    def getRechargeCount(self):
        return self._getNumber(3)

    def setRechargeCount(self, value):
        self._setNumber(3, value)

    def getIcon(self):
        return self._getResource(4)

    def setIcon(self, value):
        self._setResource(4, value)

    def getTooltipId(self):
        return self._getString(5)

    def setTooltipId(self, value):
        self._setString(5, value)

    def getIsSelected(self):
        return self._getBool(6)

    def setIsSelected(self, value):
        self._setBool(6, value)

    def getType(self):
        return self._getString(7)

    def setType(self, value):
        self._setString(7, value)

    def getOrderModifier(self):
        return self._getNumber(8)

    def setOrderModifier(self, value):
        self._setNumber(8, value)

    def getIsTokenShortage(self):
        return self._getBool(9)

    def setIsTokenShortage(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(OrderModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addNumberProperty('count', 0)
        self._addNumberProperty('timer', 0)
        self._addNumberProperty('rechargeCount', 0)
        self._addResourceProperty('icon', R.invalid())
        self._addStringProperty('tooltipId', '')
        self._addBoolProperty('isSelected', False)
        self._addStringProperty('type', '')
        self._addNumberProperty('orderModifier', 0)
        self._addBoolProperty('isTokenShortage', False)
