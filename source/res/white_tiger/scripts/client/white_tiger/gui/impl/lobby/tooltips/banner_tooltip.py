# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/banner_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.pub import ViewImpl
from helpers import dependency, time_utils
from white_tiger.gui.game_control.white_tiger_controller import WhiteTigerController
from white_tiger.gui.impl.gen.view_models.views.lobby.event_banner_view_model import EventBannerViewModel, PerformanceRiskEnum, State
from white_tiger.skeletons.economics_controller import IEconomicsController
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
_BANNER_STATE_TO_TOOLTIP_STATE = {EventBannerState.INACTIVE: State.FROZEN,
 EventBannerState.INTRO: State.INTRO,
 EventBannerState.IN_PROGRESS: State.INPROGRESS,
 EventBannerState.ANNOUNCE: State.INANNOUNCEMENT}

class EventBannerTooltipView(ViewImpl):
    _wtController = dependency.descriptor(IWhiteTigerController)
    _wtEconomicsController = dependency.descriptor(IEconomicsController)

    def __init__(self, bannerState, isAnouncement):
        settings = ViewSettings(R.views.white_tiger.mono.lobby.tooltips.banner_tooltip())
        settings.model = EventBannerViewModel()
        super(EventBannerTooltipView, self).__init__(settings)
        self._bannerState = bannerState
        self._isAnouncement = isAnouncement

    @property
    def viewModel(self):
        return super(EventBannerTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        state = _BANNER_STATE_TO_TOOLTIP_STATE.get(self._bannerState, State.INPROGRESS)
        if self._bannerState == EventBannerState.ANNOUNCE:
            timerValue = 0
        elif self._isAnouncement:
            timeToStart = self._wtController.getStartDate()
            now = time_utils.getCurrentLocalServerTimestamp()
            timerValue = timeToStart - now
            state = _BANNER_STATE_TO_TOOLTIP_STATE.get(EventBannerState.ANNOUNCE)
        else:
            timerValue = self._wtController.getLeftTimeToPrimeTimesEnd()
        super(EventBannerTooltipView, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            model.setPerformanceRisk(PerformanceRiskEnum(self._wtController.performanceRisk))
            model.setState(state)
            model.setDate(self._wtController.getStartDate())
            model.setEndDate(self._wtController.getEndDate())
            model.setFinishedLevelsCount(self._wtEconomicsController.getFinishedLevelsCount())
            model.setMaxProgressionStep(self._wtEconomicsController.getProgressionMaxLevel())
            model.setNextTimeEnable(timerValue)
