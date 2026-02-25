# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/impl/lobby/tooltips/entry_point_tooltip.py
import logging
from comp7_core.gui.impl.lobby.comp7_core_helpers.comp7_core_model_helpers import setSeasonInfo
from frameworks.wulf.view.array import fillIntsArray
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.pub import ViewImpl
from helpers.time_utils import getServerUTCTime
_logger = logging.getLogger(__name__)

class Comp7CoreEntryPointTooltip(ViewImpl):

    def __init__(self, settings, eventBanner):
        super(Comp7CoreEntryPointTooltip, self).__init__(settings)
        self._banner = eventBanner

    @property
    def _modeController(self):
        raise NotImplementedError

    @property
    def _seasonStateClazz(self):
        raise NotImplementedError

    @property
    def _seasonNameClazz(self):
        raise NotImplementedError

    @property
    def viewModel(self):
        return super(Comp7CoreEntryPointTooltip, self).getViewModel()

    def _getEvents(self):
        return ((self._modeController.onStatusUpdated, self._onStatusUpdated), (self._modeController.onStatusTick, self._onStatusTick), (self.viewModel.season.pollServerTime, self.__onPollServerTime))

    def _onLoading(self, *args, **kwargs):
        super(Comp7CoreEntryPointTooltip, self)._onLoading(*args, **kwargs)
        self._updateState()

    def _onStatusUpdated(self, _):
        self._updateState()

    def _onStatusTick(self):
        self._updateState()

    def _updateState(self):
        seasonStateClazz = self._seasonStateClazz
        bannerState = self._banner.bannerState
        if bannerState == EventBannerState.ANNOUNCE:
            seasonState = seasonStateClazz.NOTSTARTED
        elif bannerState in (EventBannerState.INTRO, EventBannerState.IN_PROGRESS):
            seasonState = seasonStateClazz.ACTIVE
        elif bannerState == EventBannerState.INACTIVE:
            seasonState = seasonStateClazz.DISABLED
        else:
            _logger.error('Unhandled bannerState = %s', bannerState)
            seasonState = seasonStateClazz.DISABLED
        ctrl = self._modeController
        season = ctrl.getCurrentSeason() or ctrl.getNextSeason() or ctrl.getPreviousSeason()
        with self.getViewModel().transaction() as tx:
            setSeasonInfo(tx.season, ctrl, seasonStateClazz, self._seasonNameClazz, season)
            tx.setTimeLeftUntilPrimeTime(self._banner.timerValue)
            tx.season.setState(seasonState)
            fillIntsArray(ctrl.getModeSettings().levels, tx.getVehicleLevels())

    def __onPollServerTime(self):
        with self.viewModel.transaction() as tx:
            tx.season.setServerTimestamp(round(getServerUTCTime()))
