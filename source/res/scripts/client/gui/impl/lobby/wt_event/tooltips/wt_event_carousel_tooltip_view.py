# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/tooltips/wt_event_carousel_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.wt_event_carousel_tooltip_view_model import WtEventCarouselTooltipViewModel
from gui.impl.pub import ViewImpl

class WtEventCarouselTooltipView(ViewImpl):
    __slots__ = ('__ticketsCount',)

    def __init__(self, ticketsCount=0):
        settings = ViewSettings(R.views.lobby.wt_event.tooltips.WtEventCarouselTooltipView())
        settings.model = WtEventCarouselTooltipViewModel()
        self.__ticketsCount = ticketsCount
        super(WtEventCarouselTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WtEventCarouselTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtEventCarouselTooltipView, self)._onLoading()
        with self.viewModel.transaction() as vModelTrx:
            vModelTrx.setQuantity(self.__ticketsCount)
