# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/order_tooltip.py
from historical_battles import hb_constants
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.shared.tooltips import ToolTipBaseData
from helpers import dependency
from frameworks.wulf import ViewSettings
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.order_tooltip_model import OrderTooltipModel
from historical_battles.gui.impl.gen.view_models.views.lobby.order_model import OrderType
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from gui.impl.pub import ViewImpl

class OrderTooltip(ViewImpl):
    __slots__ = ('__orderType', '__isPreview', '__isUsedInBattle')
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, orderType, isPreview, isUsedInBattle):
        settings = ViewSettings(R.views.historical_battles.lobby.tooltips.OrderTooltip())
        settings.model = OrderTooltipModel()
        super(OrderTooltip, self).__init__(settings)
        model = self.viewModel
        model.setIsPreview(bool(isPreview))
        model.setIsUsedInBattle(bool(isUsedInBattle))
        self.__fillOrder(model, orderType)

    @property
    def viewModel(self):
        return super(OrderTooltip, self).getViewModel()

    def __fillOrder(self, model, orderType):
        frontCoupons = self._gameEventController.frontCoupons.getGroupedFrontCoupons()
        frontCouponByType = self.__getOrderByType(frontCoupons, orderType)
        model.order.setType(hb_constants.MultiplierToOrderType.get(frontCouponByType.getModifier(), OrderType.SMALL))
        model.order.setId(frontCouponByType.getLabel())
        model.order.setCount(frontCouponByType.getCurrentCount())
        model.order.setIsActive(frontCouponByType.isActive())

    @staticmethod
    def __getOrderByType(frontCoupons, orderType):
        for frontCoupon in frontCoupons:
            if not frontCoupon or not frontCoupon.isDrawActive():
                continue
            if hb_constants.MultiplierToOrderType.get(frontCoupon.getModifier(), OrderType.SMALL).value == orderType:
                return frontCoupon


class OrderTooltipWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(OrderTooltipWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.HB_ORDER_TOOLTIP)

    def getDisplayableData(self, orderType, isPreview=True, isUsedInBattle=False):
        return DecoratedTooltipWindow(OrderTooltip(orderType, isPreview, isUsedInBattle), useDecorator=False)
