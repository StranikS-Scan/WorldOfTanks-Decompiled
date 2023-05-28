# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/stronghold/stronghold_entry_point_view.py
import typing
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.lobby.clans.clan_helpers import getStrongholdEventUrl
from gui.clans.clan_cache import g_clanCache
from gui.clans.formatters import DUMMY_UNAVAILABLE_DATA
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.stronghold.stronghold_entry_point_view_model import StrongholdEntryPointViewModel, State
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showStrongholds
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import time_utils, dependency
from skeletons.gui.shared import IItemsCache

def isStrongholdEntryPointAvailable():
    return True


class StrongholdEntryPointView(ViewImpl):
    __slots__ = ('__isSingle', '__notifier')
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.stronghold.StrongholdEntryPointView())
        settings.flags = flags
        settings.model = StrongholdEntryPointViewModel()
        super(StrongholdEntryPointView, self).__init__(settings)
        self.__isSingle = True
        self.__notifier = None
        return

    @property
    def viewModel(self):
        return super(StrongholdEntryPointView, self).getViewModel()

    def setIsSingle(self, value):
        self.__isSingle = value
        self.viewModel.setIsSingle(value)

    def _finalize(self):
        if self.__notifier is not None:
            self.__notifier.stopNotification()
            self.__notifier.clear()
            self.__notifier = None
        super(StrongholdEntryPointView, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        super(StrongholdEntryPointView, self)._onLoading(*args, **kwargs)
        self.__updateState()

    def _getEvents(self):
        return ((self.viewModel.onOpen, self.__onOpen), (g_clanCache.strongholdEventProvider.onDataReceived, self.__onEventDataReceived), (self.__itemsCache.onSyncCompleted, self.__onSyncCompleted))

    def __updateState(self):
        with self.viewModel.transaction() as tx:
            state, startTime, endTime, timeUntilUpdateState = self.__getActualStateAndTime()
            tx.setIsSingle(self.__isSingle)
            tx.setState(state)
            tx.setStartTimestamp(startTime)
            tx.setEndTimestamp(endTime)
            self.__restartNotifier(timeUntilUpdateState)

    def __restartNotifier(self, timeUntilUpdateState):
        if self.__notifier is not None:
            self.__notifier.stopNotification()
            self.__notifier.clear()
            self.__notifier = None
        self.__notifier = SimpleNotifier(lambda : timeUntilUpdateState, self.__updateState)
        self.__notifier.startNotification()
        return

    @staticmethod
    def __getActualStateAndTime():
        isRunning = g_clanCache.strongholdEventProvider.isRunning()
        eventSettings = g_clanCache.strongholdEventProvider.getSettings()
        if eventSettings is None:
            return (State.DATAERROR,
             0,
             0,
             0)
        timeNow = time_utils.getServerUTCTime()
        eventEnd = eventSettings.getVisibleEndDate()
        if g_clanCache.isInClan and isRunning:
            clanInfo = g_clanCache.strongholdEventProvider.getClanPrimeTime()
            if clanInfo is None:
                return (State.DATAERROR,
                 0,
                 0,
                 0)
            primeTimeStart = clanInfo.getPrimeTimeStart()
            primeTimeEnd = clanInfo.getPrimeTimeEnd()
            hasPrimeTime = primeTimeStart is not None and primeTimeStart != DUMMY_UNAVAILABLE_DATA
            if not hasPrimeTime:
                return (State.PRIMETIMENOTCHOSEN,
                 eventSettings.getVisibleStartDate(),
                 eventEnd,
                 time_utils.ONE_HOUR)
            primeStartDayStart, _ = time_utils.getDayTimeBoundsForLocal(primeTimeStart)
            primeEndDayStart, _ = time_utils.getDayTimeBoundsForLocal(primeTimeEnd)
            todayStart, todayEnd = time_utils.getDayTimeBoundsForLocal()
            if primeTimeStart <= timeNow <= primeTimeEnd:
                return (State.PRIMETIMENOW,
                 primeTimeStart,
                 primeTimeEnd,
                 primeTimeEnd - timeNow)
            if todayStart == primeStartDayStart and primeTimeEnd > timeNow:
                return (State.PRIMETIMETODAY,
                 primeTimeStart,
                 primeTimeEnd,
                 primeTimeStart - timeNow if primeTimeStart < eventEnd else eventEnd - timeNow)
            if primeStartDayStart != primeEndDayStart and primeTimeEnd < timeNow:
                primeTimeStart = primeTimeStart + time_utils.ONE_DAY
                return (State.PRIMETIMETODAY,
                 primeTimeStart,
                 primeTimeEnd + time_utils.ONE_DAY,
                 primeTimeStart - timeNow if primeTimeStart < eventEnd else eventEnd - timeNow)
            return (State.PRIMETIMETOMORROW,
             primeTimeStart,
             primeTimeEnd,
             todayEnd - timeNow if todayEnd < eventEnd else eventEnd - timeNow)
        elif isRunning:
            return (State.STARTED,
             eventSettings.getVisibleStartDate(),
             eventEnd,
             eventEnd - timeNow)
        else:
            return (State.NOTSTARTED,
             eventSettings.getVisibleStartDate(),
             eventEnd,
             eventSettings.getVisibleStartDate() - timeNow) if eventSettings.getVisibleStartDate() > timeNow else (State.ENDED,
             0,
             0,
             0)

    @staticmethod
    def __onOpen():
        showStrongholds(getStrongholdEventUrl())

    def __onEventDataReceived(self, _, __):
        self.__updateState()

    def __onSyncCompleted(self, _, diff):
        self.__updateState()
