# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/orders_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.order_model import OrderModel

class OrdersModel(ViewModel):
    __slots__ = ('onBuyOrdersPressed', 'onGetOrdersPressed', 'onIconAnimationStart', 'onIconAnimationFinish', 'onBorderAnimationStart', 'onBorderAnimationFinish')

    def __init__(self, properties=3, commands=6):
        super(OrdersModel, self).__init__(properties=properties, commands=commands)

    def getOrderCountdown(self):
        return self._getNumber(0)

    def setOrderCountdown(self, value):
        self._setNumber(0, value)

    def getOrders(self):
        return self._getArray(1)

    def setOrders(self, value):
        self._setArray(1, value)

    @staticmethod
    def getOrdersType():
        return OrderModel

    def getSelectedOrderId(self):
        return self._getString(2)

    def setSelectedOrderId(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(OrdersModel, self)._initialize()
        self._addNumberProperty('orderCountdown', 10800)
        self._addArrayProperty('orders', Array())
        self._addStringProperty('selectedOrderId', '')
        self.onBuyOrdersPressed = self._addCommand('onBuyOrdersPressed')
        self.onGetOrdersPressed = self._addCommand('onGetOrdersPressed')
        self.onIconAnimationStart = self._addCommand('onIconAnimationStart')
        self.onIconAnimationFinish = self._addCommand('onIconAnimationFinish')
        self.onBorderAnimationStart = self._addCommand('onBorderAnimationStart')
        self.onBorderAnimationFinish = self._addCommand('onBorderAnimationFinish')
