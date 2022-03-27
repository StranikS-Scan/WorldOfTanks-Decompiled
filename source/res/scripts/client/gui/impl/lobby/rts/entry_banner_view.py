# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/entry_banner_view.py
import typing
import logging
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.rts.entry_banner_view_model import EntryBannerViewModel, State
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from helpers import dependency, time_utils
from skeletons.gui.game_control import IRTSBattlesController
if typing.TYPE_CHECKING:
    from season_common import GameSeason
_logger = logging.getLogger(__name__)

class EntryBannerView(ViewImpl):
    __slots__ = ()
    __rtsBattlesController = dependency.descriptor(IRTSBattlesController)

    def __init__(self, flags):
        settings = ViewSettings(layoutID=R.views.lobby.rts.EntryBannerView(), flags=flags, model=EntryBannerViewModel())
        super(EntryBannerView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EntryBannerView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        self.viewModel.onClick += self._onClicked
        self.__rtsBattlesController.onUpdated += self._fillModel

    def _finalize(self):
        self.viewModel.onClick -= self._onClicked
        self.__rtsBattlesController.onUpdated -= self._fillModel

    def _onLoading(self, *args, **kwargs):
        self._fillModel()

    def _fillModel(self):
        _logger.debug('EntryBannerView: _onLoading')
        rtsController = self.__rtsBattlesController
        currentSeason = rtsController.getCurrentSeason()
        if currentSeason is None:
            _logger.error('EntryBannerView: banner loaded when RTS is not in active season!')
            return
        else:
            currentCycleInfo = currentSeason.getCycleInfo()
            now = _getNow()
            startDate = 0
            endDate = 0
            if currentCycleInfo:
                startDate = currentCycleInfo.startDate - now
                endDate = currentCycleInfo.endDate - now
                if rtsController.hasAvailablePrimeTimeServers():
                    state = State.AVAILABLE
                    eventEndTimestamp = rtsController.getEventEndTimestamp()
                    if eventEndTimestamp:
                        endDate = eventEndTimestamp - now
                else:
                    hasPrimetimeLeft = rtsController.hasPrimeTimesLeftForCurrentCycle()
                    _logger.info(hasPrimetimeLeft)
                    if hasPrimetimeLeft:
                        startDate = hasPrimetimeLeft.getNextPeriodStart(now, currentSeason.getCycleEndDate()) - now
                        state = State.PAUSED
                    else:
                        state = State.FINISHED
                    if not rtsController.hasConfiguredPrimeTimeServers():
                        state = State.PAUSED
            else:
                firstCycle = currentSeason.getFirstCycleInfo()
                firstCycleNotStarted = firstCycle.startDate > now
                if firstCycleNotStarted:
                    startDate = firstCycle.startDate - now
                    state = State.ANNOUNCE
                else:
                    state = State.FINISHED
            _logger.debug('EntryBannerView: state: %s, start: %s, end: %s', state, startDate, endDate)
            with self.viewModel.transaction() as tx:
                tx.setStartDate(startDate)
                tx.setEndDate(endDate)
                tx.setState(state)
            return

    def _onClicked(self):
        self.__rtsBattlesController.enterRTSPrebattle()


def _getNow():
    return time_utils.getCurrentLocalServerTimestamp()


def isRTSEntryBannerAvailable():
    rtsBattlesController = dependency.instance(IRTSBattlesController)
    return rtsBattlesController.isAvailable()
