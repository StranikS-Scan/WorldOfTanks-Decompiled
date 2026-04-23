# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/order_widget_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.order_model import OrderModel

class OrderWidgetModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=2, commands=1):
        super(OrderWidgetModel, self).__init__(properties=properties, commands=commands)

    def getFrontType(self):
        return self._getString(0)

    def setFrontType(self, value):
        self._setString(0, value)

    def getOrders(self):
        return self._getArray(1)

    def setOrders(self, value):
        self._setArray(1, value)

    @staticmethod
    def getOrdersType():
        return OrderModel

    def _initialize(self):
        super(OrderWidgetModel, self)._initialize()
        self._addStringProperty('frontType', '')
        self._addArrayProperty('orders', Array())
        self.onClick = self._addCommand('onClick')
