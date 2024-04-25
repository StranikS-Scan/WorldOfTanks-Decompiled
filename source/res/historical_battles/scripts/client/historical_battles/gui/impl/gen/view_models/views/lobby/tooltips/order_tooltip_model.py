# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/tooltips/order_tooltip_model.py
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.order_model import OrderModel

class OrderTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(OrderTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def order(self):
        return self._getViewModel(0)

    @staticmethod
    def getOrderType():
        return OrderModel

    def getIsPreview(self):
        return self._getBool(1)

    def setIsPreview(self, value):
        self._setBool(1, value)

    def getIsUsedInBattle(self):
        return self._getBool(2)

    def setIsUsedInBattle(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(OrderTooltipModel, self)._initialize()
        self._addViewModelProperty('order', OrderModel())
        self._addBoolProperty('isPreview', False)
        self._addBoolProperty('isUsedInBattle', False)
