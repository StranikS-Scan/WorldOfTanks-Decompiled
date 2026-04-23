# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/tooltips/hb_order_widget_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.order_model import OrderModel

class HbOrderWidgetTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(HbOrderWidgetTooltipModel, self).__init__(properties=properties, commands=commands)

    def getOrders(self):
        return self._getArray(0)

    def setOrders(self, value):
        self._setArray(0, value)

    @staticmethod
    def getOrdersType():
        return OrderModel

    def _initialize(self):
        super(HbOrderWidgetTooltipModel, self)._initialize()
        self._addArrayProperty('orders', Array())
