# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/lobby/order_widget.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.lobby.hangar_selectable_view import HangarSelectableView
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from historical_battles.gui.impl.gen.view_models.views.lobby.order_widget_model import OrderWidgetModel
from helpers import dependency
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.gui.shared.event_dispatcher import showHBOrderView
from historical_battles.gui.impl.gen.view_models.views.lobby.order_model import OrderModel, OrderType
from gui.impl.pub.tooltip_window import ToolTipWindow
from historical_battles.gui.impl.lobby.tooltips.hb_order_widget_tooltip import HbOrderWidgetTooltip
from historical_battles.gui.impl.lobby.tooltips.order_tooltip import OrderTooltip
_logger = logging.getLogger(__name__)

class OrderWidget(InjectComponentAdaptor):

    def _makeInjectView(self):
        return OrderWidgetView(R.views.historical_battles.lobby.OrderWidget())


class OrderWidgetView(HangarSelectableView):
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = OrderWidgetModel()
        super(OrderWidgetView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(OrderWidgetView, self).getViewModel()

    def _getEvents(self):
        return ((self.__gameEventController.frontDataUpdated, self.__onFrontDataUpdated),)

    def _onLoading(self, *args, **kwargs):
        super(OrderWidgetView, self)._onLoading(*args, **kwargs)
        self.__setFrontType()
        self.__fillOrders()
        self.__addEventListeners()

    def __setFrontType(self):
        currentFront = self.__gameEventController.frontController.getSelectedFront()
        with self.viewModel.transaction() as model:
            model.setFrontType(currentFront.getName())

    def createToolTip(self, event):
        content = None
        if event.contentID == R.views.historical_battles.lobby.tooltips.OrderWidgetTooltip():
            content = HbOrderWidgetTooltip()
        elif event.contentID == R.views.historical_battles.lobby.tooltips.OrderTooltip():
            orderType = event.getArgument('orderType')
            showStatus = event.getArgument('showStatus')
            content = OrderTooltip(orderType, showStatus)
        if content:
            window = ToolTipWindow(event, content, self.getParentWindow())
            window.load()
            window.move(event.mouse.positionX, event.mouse.positionY)
        return super(OrderWidgetView, self).createToolTip(event)

    def __fillOrders(self):
        with self.getViewModel().transaction() as model:
            ordersModel = model.getOrders()
            ordersModel.clear()
            orders = self.__gameEventController.frontCoupons.getGroupedFrontCoupons()
            for item in orders:
                if not item.isDrawActive():
                    continue
                orderModel = OrderModel()
                orderModel.setCount(item.getCurrentCount())
                orderModel.setType(OrderType(item.getLabel()))
                ordersModel.addViewModel(orderModel)

            ordersModel.invalidate()

    def __onFrontDataUpdated(self, *_):
        self.__setFrontType()

    def _finalize(self):
        self.__removeEventListeners()
        super(OrderWidgetView, self)._finalize()

    def __addEventListeners(self):
        self.viewModel.onClick += self.__onClick

    def __removeEventListeners(self):
        self.viewModel.onClick -= self.__onClick

    @staticmethod
    def __onClick():
        showHBOrderView()
