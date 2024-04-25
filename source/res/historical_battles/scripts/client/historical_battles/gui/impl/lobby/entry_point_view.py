# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/entry_point_view.py
from adisp import adisp_process
from frameworks.wulf import ViewFlags, ViewSettings
from Event import Event, EventManager
from historical_battles.gui.impl.gen.view_models.views.lobby.entry_point_view_model import EntryPointViewModel, EventState, PerformanceRiskEnum
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.Scaleform.Waiting import Waiting
from historical_battles.gui.prb_control.prb_config import PREBATTLE_ACTION_NAME
from historical_battles.gui.impl.lobby.mode_selector.items.historical_battles_mode_selector_item import PERFORMANCE_MAP
from historical_battles.gui.impl.lobby.tooltips.entry_point_tooltip import EntryPointTooltip
from helpers import dependency, time_utils
from helpers.CallbackDelayer import CallbackDelayer
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache

class EntryPointView(ViewImpl):
    _eventsCache = dependency.descriptor(IEventsCache)
    _gameEventController = dependency.descriptor(IGameEventController)
    _BANNER_WAIT_TICK = 0.2

    def __init__(self):
        settings = ViewSettings(R.views.historical_battles.lobby.EntryPointView())
        settings.flags = ViewFlags.VIEW
        settings.model = EntryPointViewModel()
        super(EntryPointView, self).__init__(settings)
        self.__callbackDelayer = None
        self._em = EventManager()
        self.onAnimationFinished = Event(self._em)
        return

    @property
    def viewModel(self):
        return super(EntryPointView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return EntryPointTooltip() if contentID == R.views.historical_battles.lobby.tooltips.EntryPointTooltip() else super(EntryPointView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(EntryPointView, self)._onLoading(*args, **kwargs)
        self.viewModel.onClick += self.__onClickBanner
        self.viewModel.onShowingAnimationFinish += self.onAnimationFinished
        self._eventsCache.onSyncCompleted += self.__update
        self._gameEventController.onGameParamsChanged += self._onGameParamsChanged
        self.__update()

    def _onLoaded(self, *args, **kwargs):
        super(EntryPointView, self)._onLoaded(*args, **kwargs)
        self.__callbackDelayer = CallbackDelayer()
        self.__callbackDelayer.delayCallback(self._BANNER_WAIT_TICK, self.__setBannerReady)

    def _finalize(self):
        if self.__callbackDelayer:
            self.__callbackDelayer.clearCallbacks()
        self.viewModel.onClick -= self.__onClickBanner
        self.viewModel.onShowingAnimationFinish -= self.onAnimationFinished
        self._eventsCache.onSyncCompleted -= self.__update
        self._gameEventController.onGameParamsChanged -= self._onGameParamsChanged
        super(EntryPointView, self)._finalize()

    def _onGameParamsChanged(self):
        if not self._gameEventController.isEnabled():
            self.destroy()

    def __update(self):
        with self.viewModel.transaction() as tx:
            self.__fillViewModel(tx)

    def __onClickBanner(self):
        ct, st, et = self.__getEventTimes()
        if st < ct < et:
            self.__showEventHangar()

    @adisp_process
    def __showEventHangar(self):
        yield g_prbLoader.getDispatcher().doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.HISTORICAL_BATTLES))

    def __getEventTimes(self):
        return (time_utils.getCurrentLocalServerTimestamp(), self._gameEventController.getEventStartTime(), self._gameEventController.getEventFinishTime())

    def __fillViewModel(self, tx):
        ct, st, et = self.__getEventTimes()
        eventState = EventState.ACTIVE if ct > st else EventState.ANNOUNCE
        currentPerformanceGroup = self._gameEventController.getPerformanceGroup()
        tx.setPerformanceRisk(PERFORMANCE_MAP.get(currentPerformanceGroup, PerformanceRiskEnum.LOWRISK))
        if eventState is EventState.ANNOUNCE:
            tx.setTimeLeft(int(st))
        if eventState is EventState.ACTIVE:
            tx.setTimeLeft(int(et))
        tx.setEventState(eventState)

    def __setBannerReady(self):
        if not Waiting.isVisible():
            self.viewModel.setIsAnimated(True)
            return None
        else:
            return self._BANNER_WAIT_TICK
