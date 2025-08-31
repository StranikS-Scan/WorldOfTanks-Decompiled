# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/wt_event_ticket_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.wt_event_ticket_tooltip_view_model import WtEventTicketTooltipViewModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IWhiteTigerController
from white_tiger.gui.impl.gen.view_models.views.common.wt_common_consts import WTVehicleType

class WtEventTicketTooltipView(ViewImpl):
    __slots__ = ('__wtVehicleType',)
    __eventController = dependency.descriptor(IWhiteTigerController)

    def __init__(self, wtVehicleType=WTVehicleType.BOSS.value):
        settings = ViewSettings(R.views.white_tiger.lobby.tooltips.TicketTooltipView())
        settings.model = WtEventTicketTooltipViewModel()
        self.__wtVehicleType = wtVehicleType
        super(WtEventTicketTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WtEventTicketTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtEventTicketTooltipView, self)._onLoading()
        quantity = self.__eventController.getTicketCount() if self.__wtVehicleType == WTVehicleType.BOSS.value else self.__eventController.getTicket2025Count()
        self.viewModel.setQuantity(quantity)
        self.viewModel.setWtVehicleType(self.__wtVehicleType)
