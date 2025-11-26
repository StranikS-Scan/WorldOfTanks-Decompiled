# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/stronghold_event/tooltips/stronghold_event_banner_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.stronghold_event.stronghold_event_banner_tooltip_view_model import StrongholdEventBannerTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class StrongholdEventBannerTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.mono.stronghold_event.tooltips.event_banner_tooltip())
        settings.model = StrongholdEventBannerTooltipViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(StrongholdEventBannerTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(StrongholdEventBannerTooltip, self).getViewModel()

    def _onLoading(self, state, startDate, endDate):
        with self.viewModel.transaction() as vm:
            vm.setState(state)
            vm.setStartDate(startDate)
            vm.setEndDate(endDate)
