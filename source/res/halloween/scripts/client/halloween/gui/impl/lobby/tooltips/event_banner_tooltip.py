# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/tooltips/event_banner_tooltip.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.mode_performance_model import PerformanceRiskEnum
from gui.impl.pub import ViewImpl
from helpers import dependency, time_utils
from halloween.gui.impl.gen.view_models.views.lobby.tooltips.event_banner_view_model import EventBannerViewModel
from halloween.gui.shared.utils.performance_analyzer import PerformanceGroup
from halloween.skeletons.halloween_controller import IHalloweenController
PERFORMANCE_MAP = {PerformanceGroup.LOW_RISK: PerformanceRiskEnum.LOWRISK,
 PerformanceGroup.MEDIUM_RISK: PerformanceRiskEnum.MEDIUMRISK,
 PerformanceGroup.HIGH_RISK: PerformanceRiskEnum.HIGHRISK}

class EventBannerTooltipView(ViewImpl):
    hwController = dependency.descriptor(IHalloweenController)
    __slots__ = ('__performanceRisk',)

    def __init__(self, layoutID=R.views.halloween.mono.lobby.tooltips.banner_tooltip()):
        settings = ViewSettings(layoutID)
        settings.model = EventBannerViewModel()
        super(EventBannerTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EventBannerTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EventBannerTooltipView, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            model.setPerformanceRisk(PERFORMANCE_MAP.get(self.hwController.getPerformanceGroup(), PerformanceRiskEnum.LOWRISK))
            model.setDate(time_utils.getServerUTCTime())
            model.setEndDate(self.hwController.getModeSettings().endDate)
