# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/order_exchange_model.py
from gui.impl.gen.view_models.views.lobby.secret_event.order_model import OrderModel

class OrderExchangeModel(OrderModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(OrderExchangeModel, self).__init__(properties=properties, commands=commands)

    def getTokenID(self):
        return self._getString(10)

    def setTokenID(self, value):
        self._setString(10, value)

    def getTokenCount(self):
        return self._getNumber(11)

    def setTokenCount(self, value):
        self._setNumber(11, value)

    def getOrderExchange(self):
        return self._getNumber(12)

    def setOrderExchange(self, value):
        self._setNumber(12, value)

    def getTokenExchange(self):
        return self._getNumber(13)

    def setTokenExchange(self, value):
        self._setNumber(13, value)

    def _initialize(self):
        super(OrderExchangeModel, self)._initialize()
        self._addStringProperty('tokenID', '')
        self._addNumberProperty('tokenCount', 0)
        self._addNumberProperty('orderExchange', 0)
        self._addNumberProperty('tokenExchange', 0)
