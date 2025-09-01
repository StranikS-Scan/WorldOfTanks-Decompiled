# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/ticket_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from white_tiger.skeletons.economics_controller import IEconomicsController
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.ticket_tooltip_view_model import TicketTooltipViewModel

class TicketTooltipView(ViewImpl):
    __slots__ = ()
    __economicsCtrl = dependency.descriptor(IEconomicsController)
    _layout_id = R.views.white_tiger.mono.lobby.tooltips.ticket_tooltip

    def __init__(self):
        settings = ViewSettings(self._layout_id())
        settings.model = TicketTooltipViewModel()
        super(TicketTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TicketTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(TicketTooltipView, self)._onLoading()
        self.viewModel.setQuantity(self.__economicsCtrl.getTicketCount())


class TicketToolTipViewLegacy(TicketTooltipView):
    __slots__ = ()
    _layout_id = R.views.white_tiger.lobby.tooltips.TicketTooltipView
