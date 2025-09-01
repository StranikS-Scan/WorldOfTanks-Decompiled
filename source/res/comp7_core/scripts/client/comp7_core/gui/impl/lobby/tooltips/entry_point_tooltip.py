# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/impl/lobby/tooltips/entry_point_tooltip.py
from comp7_core.gui.impl.lobby.comp7_core_helpers.comp7_core_shared import getModeSeasonState
from comp7_core.gui.impl.lobby.comp7_core_helpers.comp7_core_model_helpers import setSeasonInfo
from gui.impl.pub import ViewImpl
from helpers.time_utils import getServerUTCTime

class Comp7CoreEntryPointTooltip(ViewImpl):

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
        with self.viewModel.transaction() as tx:
            season = self._modeController.getCurrentSeason() or self._modeController.getNextSeason() or self._modeController.getPreviousSeason()
            setSeasonInfo(tx.season, self._modeController, self._seasonStateClazz, self._seasonNameClazz, season)
            periodInfo = self._modeController.getPeriodInfo()
            tx.setTimeLeftUntilPrimeTime(periodInfo.primeDelta)
            tx.season.setState(getModeSeasonState(self._modeController, self._seasonStateClazz))
            levelsArr = tx.getVehicleLevels()
            levelsArr.clear()
            for level in self._modeController.getModeSettings().levels:
                levelsArr.addNumber(level)

            levelsArr.invalidate()

    def __onPollServerTime(self):
        with self.viewModel.transaction() as tx:
            tx.season.setServerTimestamp(round(getServerUTCTime()))
