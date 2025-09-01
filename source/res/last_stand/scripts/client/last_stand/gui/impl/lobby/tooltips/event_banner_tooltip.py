# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/tooltips/event_banner_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_performance_model import PerformanceRiskEnum
from gui.impl.pub import ViewImpl
from helpers import dependency, time_utils
from last_stand.gui.impl.gen.view_models.views.lobby.event_banner_view_model import EventBannerViewModel
from last_stand.gui.shared.utils.performance_analyzer import PerformanceGroup
from last_stand.skeletons.ls_controller import ILSController
PERFORMANCE_MAP = {PerformanceGroup.LOW_RISK: PerformanceRiskEnum.LOWRISK,
 PerformanceGroup.MEDIUM_RISK: PerformanceRiskEnum.MEDIUMRISK,
 PerformanceGroup.HIGH_RISK: PerformanceRiskEnum.HIGHRISK}

class EventBannerTooltipView(ViewImpl):
    lsCtrl = dependency.descriptor(ILSController)
    __slots__ = ('__performanceRisk',)

    def __init__(self, layoutID=R.views.last_stand.mono.lobby.tooltips.banner_tooltip()):
        settings = ViewSettings(layoutID)
        settings.model = EventBannerViewModel()
        super(EventBannerTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EventBannerTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EventBannerTooltipView, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            model.setPerformanceRisk(PERFORMANCE_MAP.get(self.lsCtrl.getPerformanceGroup(), PerformanceRiskEnum.LOWRISK))
            model.setDate(time_utils.getServerUTCTime())
            model.setEndDate(self.lsCtrl.getModeSettings().endDate)
