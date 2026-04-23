# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/hb_order_widget_tooltip.py
from frameworks.wulf import ViewSettings
from helpers import dependency
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from historical_battles.gui.impl.gen.view_models.views.lobby.order_model import OrderModel, OrderType
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.hb_order_widget_tooltip_model import HbOrderWidgetTooltipModel
from historical_battles.skeletons.gui.game_event_controller import IGameEventController

class HbOrderWidgetTooltip(ViewImpl):
    __slots__ = ()
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        settings = ViewSettings(R.views.historical_battles.lobby.tooltips.OrderWidgetTooltip())
        settings.model = HbOrderWidgetTooltipModel()
        super(HbOrderWidgetTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(HbOrderWidgetTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.getViewModel().transaction() as model:
            self.__fillOrders(model)

    def __fillOrders(self, model):
        ordersModel = model.getOrders()
        ordersModel.clear()
        orders = self.__gameEventController.frontCoupons.getGroupedFrontCoupons()
        for order in orders:
            if not order.isDrawActive():
                continue
            orderModel = OrderModel()
            orderModel.setId(order.getLabel())
            orderModel.setCount(order.getCurrentCount())
            orderModel.setType(OrderType(order.getLabel()))
            ordersModel.addViewModel(orderModel)

        ordersModel.invalidate()
