# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/ten_years_countdown/ten_years_countdown_entry_point.py
import time
from enum import Enum
from frameworks.wulf import ViewFlags, ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.backport import getTillTimeStringByRClass
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.ten_years_countdown.ten_years_countdown_entry_point_model import TenYearsCountdownEntryPointModel
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.money import Currency
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency, time_utils
from skeletons.gui.game_control import ITenYearsCountdownController, IWalletController
from skeletons.gui.shared import IItemsCache
from gui.shared.event_dispatcher import showTenYearsCountdownOverlay
EVENT_COINS_SYNCING = 0
EVENT_COINS_NOT_AVAILABLE = 1

class NotifierStates(Enum):
    ACTIVE_PHASE_FINISH = 1
    NEXT_ACTIVE_PHASE_START = 2
    EVENT_FINISH = 3
    ENDED = 4


_ENABLED_EVENT_NOTIFIER_STATES = (NotifierStates.ACTIVE_PHASE_FINISH, NotifierStates.NEXT_ACTIVE_PHASE_START, NotifierStates.EVENT_FINISH)

class TenYearsCountdownEntryPoint(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __tenYearsCountdown = dependency.descriptor(ITenYearsCountdownController)
    __wallet = dependency.descriptor(IWalletController)
    __slots__ = ('__periodicNotifier', '__notifierState', '__blockNumber', '__updateAnimationMethod')

    def __init__(self, updateAnimationMethod=None, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.ten_years_countdown.TenYearsCountdownEntryPoint())
        settings.flags = flags
        settings.model = TenYearsCountdownEntryPointModel()
        super(TenYearsCountdownEntryPoint, self).__init__(settings)
        self.__periodicNotifier = None
        self.__blockNumber = 0
        self.__notifierState = None
        self.__updateAnimationMethod = updateAnimationMethod
        return

    @property
    def viewModel(self):
        return super(TenYearsCountdownEntryPoint, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(TenYearsCountdownEntryPoint, self)._onLoading(*args, **kwargs)
        self.__tenYearsCountdown.onEventStateChanged += self.__reinitialize
        self.__tenYearsCountdown.onBlocksDataValidityChanged += self.__reinitialize
        self.__initialize()

    def _finalize(self):
        self.__tenYearsCountdown.onEventStateChanged -= self.__reinitialize
        self.__tenYearsCountdown.onBlocksDataValidityChanged -= self.__reinitialize
        self.__tenYearsCountdown.onEventDataUpdated -= self.__reinitializeAfterEventUpdated
        self.__clear()
        self.__updateAnimationMethod = None
        super(TenYearsCountdownEntryPoint, self)._finalize()
        return

    def __initialize(self):
        if self.__tenYearsCountdown.isEventInProgress() and self.__tenYearsCountdown.isBlocksDataValid():
            self.__addListeners()
            self.__initNotifier()
            self.__updateModel()

    def __clear(self):
        self.__resetPeriodicNotifier()
        self.__notifierState = None
        self.__blockNumber = 0
        self.__removeListeners()
        return

    def __reinitialize(self):
        self.__tenYearsCountdown.onEventDataUpdated += self.__reinitializeAfterEventUpdated

    def __reinitializeAfterEventUpdated(self):
        self.__tenYearsCountdown.onEventDataUpdated -= self.__reinitializeAfterEventUpdated
        self.__clear()
        self.__initialize()

    def __addListeners(self):
        self.viewModel.onActionClick += self.__onClick
        self.__tenYearsCountdown.onEventBlockChanged += self.__initNotifier
        self.__tenYearsCountdown.onEventBlockChanged += self.__updateModel
        self.__tenYearsCountdown.onActivePhasesDatesChanged += self.__updateTimer
        self.__tenYearsCountdown.onEventFinishChanged += self.__updateTimer
        self.__wallet.onWalletStatusChanged += self.__updateBalance
        g_clientUpdateManager.addCurrencyCallback(Currency.EVENT_COIN, self.__updateBalance)

    def __removeListeners(self):
        self.viewModel.onActionClick -= self.__onClick
        self.__tenYearsCountdown.onEventBlockChanged -= self.__initNotifier
        self.__tenYearsCountdown.onEventBlockChanged -= self.__updateModel
        self.__tenYearsCountdown.onActivePhasesDatesChanged -= self.__updateTimer
        self.__tenYearsCountdown.onEventFinishChanged -= self.__updateTimer
        self.__wallet.onWalletStatusChanged -= self.__updateBalance
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            model.setCoinIcon(R.images.gui.maps.icons.library.EventCoinIconBig())
            self.__updateBalance(model=model)
            self.__updateTimer(model=model)

    @replaceNoneKwargsModel
    def __updateBalance(self, value=None, model=None):
        if self.__wallet.status in (EVENT_COINS_SYNCING, EVENT_COINS_NOT_AVAILABLE):
            model.setBalance(backport.text(R.strings.ten_year_countdown.entry_point.event_coins_miss()))
        else:
            model.setBalance(backport.getIntegralFormat(self.__itemsCache.items.stats.eventCoin))

    @replaceNoneKwargsModel
    def __updateTimer(self, model=None):
        if self.__notifierState != NotifierStates.ENDED:
            timeLeft = self.__getTimeLeft()
            if timeLeft == 0:
                self.__onBlockStateChanged()
                timeLeft = self.__getTimeLeft()
            timer = self.__getTimer(timeLeft)
            model.setTimer(timer)
            isTimerPaused = self.__notifierState != NotifierStates.ACTIVE_PHASE_FINISH
            model.setIsTimerPaused(isTimerPaused)
            if callable(self.__updateAnimationMethod):
                self.__updateAnimationMethod(not isTimerPaused)
            isBlockLast = self.__notifierState == NotifierStates.EVENT_FINISH
            timerText = ''
            if isTimerPaused:
                if not isBlockLast:
                    block = self.__blockNumber + 1
                    timerText = backport.text(R.strings.ten_year_countdown.entry_point.start_timer.text(), value=block)
                else:
                    timerText = backport.text(R.strings.ten_year_countdown.entry_point.event_finish_timer.text())
            model.setTimerText(timerText)
        else:
            timerText = backport.text(R.strings.ten_year_countdown.entry_point.event_finish_timer.text())
            model.setTimerText(timerText)
            timer = backport.text(R.strings.ten_year_countdown.entry_point.event_finish_timer.lessDay(), value=0)
            model.setTimer(timer)
            model.setIsTimerPaused(True)

    def __resetPeriodicNotifier(self):
        if self.__periodicNotifier:
            self.__periodicNotifier.stopNotification()
            self.__periodicNotifier.clear()
            self.__periodicNotifier = None
        return

    def __updateNotifier(self):
        self.__resetPeriodicNotifier()
        self.__updateNotifierState()
        if self.__notifierState != NotifierStates.ENDED:
            self.__periodicNotifier = self.__createNotifier()
            if self.__periodicNotifier is not None:
                self.__periodicNotifier.startNotification()
        return

    def __updateNotifierState(self):
        if self.__notifierState == NotifierStates.ACTIVE_PHASE_FINISH:
            if self.__blockNumber >= self.__tenYearsCountdown.getBlocksCount():
                self.__notifierState = NotifierStates.EVENT_FINISH
                self.__blockNumber = self.__tenYearsCountdown.getBlocksCount()
            else:
                self.__notifierState = NotifierStates.NEXT_ACTIVE_PHASE_START
        else:
            if self.__notifierState == NotifierStates.EVENT_FINISH:
                self.__notifierState = NotifierStates.ENDED
                self.__resetPeriodicNotifier()
                return
            self.__blockNumber += 1
            if self.__blockNumber > self.__tenYearsCountdown.getBlocksCount():
                self.__notifierState = NotifierStates.ENDED
                self.__resetPeriodicNotifier()
                self.__blockNumber -= 1
                return
            self.__notifierState = NotifierStates.ACTIVE_PHASE_FINISH

    def __onBlockStateChanged(self):
        self.__updateNotifier()
        isBlockActive = self.__notifierState == NotifierStates.ACTIVE_PHASE_FINISH
        if callable(self.__updateAnimationMethod):
            self.__updateAnimationMethod(isStageActive=isBlockActive)

    def __initNotifier(self):
        self.__initNotifierState()
        self.__resetPeriodicNotifier()
        self.__periodicNotifier = self.__createNotifier()
        if self.__periodicNotifier is not None:
            self.__periodicNotifier.startNotification()
        return

    def __initNotifierState(self):
        self.__blockNumber = self.__tenYearsCountdown.getCurrentBlockNumber()
        if self.__tenYearsCountdown.isCurrentBlockActive():
            self.__notifierState = NotifierStates.ACTIVE_PHASE_FINISH
        elif self.__blockNumber == self.__tenYearsCountdown.getBlocksCount():
            self.__notifierState = NotifierStates.EVENT_FINISH
        else:
            self.__notifierState = NotifierStates.NEXT_ACTIVE_PHASE_START

    def __createNotifier(self):
        return None if self.__notifierState not in _ENABLED_EVENT_NOTIFIER_STATES else PeriodicNotifier(self.__getTimeLeft, self.__updateTimer, self.__getPeriods())

    def __getPeriods(self):
        return (time_utils.QUARTER,) if self.__notifierState in _ENABLED_EVENT_NOTIFIER_STATES else ()

    def __getTimeLeft(self):
        if self.__notifierState == NotifierStates.ACTIVE_PHASE_FINISH:
            event = self.__tenYearsCountdown.getActivePhaseDates(self.__blockNumber).finish
        elif self.__notifierState == NotifierStates.NEXT_ACTIVE_PHASE_START:
            event = self.__tenYearsCountdown.getActivePhaseDates(self.__blockNumber + 1).start
        else:
            event = self.__tenYearsCountdown.getEventFinish()
        timeLeft = int(event - time_utils.getServerUTCTime())
        return max(0, timeLeft)

    def __getTimer(self, timeLeft):
        timer = ''
        if self.__notifierState == NotifierStates.ACTIVE_PHASE_FINISH:
            timer = getTillTimeStringByRClass(timeLeft, R.strings.ten_year_countdown.entry_point.finish_timer)
        elif self.__notifierState in (NotifierStates.NEXT_ACTIVE_PHASE_START, NotifierStates.EVENT_FINISH):
            if self.__notifierState == NotifierStates.NEXT_ACTIVE_PHASE_START:
                timerClass = R.strings.ten_year_countdown.entry_point.start_timer
            else:
                timerClass = R.strings.ten_year_countdown.entry_point.event_finish_timer
            if timeLeft >= time_utils.ONE_DAY:
                timeLeft = time.gmtime(timeLeft - time_utils.ONE_DAY).tm_yday
                timerRes = timerClass.days()
            else:
                timeLeft = time.gmtime(timeLeft).tm_hour
                timerRes = timerClass.lessDay()
            timer = backport.text(timerRes, value=timeLeft)
        return timer

    def __onClick(self):
        showTenYearsCountdownOverlay()
