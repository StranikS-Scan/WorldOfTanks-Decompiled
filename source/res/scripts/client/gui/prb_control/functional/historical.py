# Embedded file name: scripts/client/gui/prb_control/functional/historical.py
import BigWorld
from adisp import process
from constants import QUEUE_TYPE
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_DEBUG, LOG_ERROR
from PlayerEvents import g_playerEvents
from gui import SystemMessages
from gui import DialogsInterface
from gui.game_control import g_instance as g_gameCtrl
from gui.prb_control.context import PrbCtrlRequestCtx, pre_queue_ctx
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.server_events import g_eventsCache
from gui.prb_control import isParentControlActivated, isInHistoricalQueue
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.functional.default import PreQueueFunctional
from gui.prb_control.functional.interfaces import IStatefulFunctional, IPrbEntry
from gui.prb_control.formatters import messages
from gui.prb_control.settings import QUEUE_EVENT_TYPE, PREQUEUE_SETTING_NAME, PREBATTLE_ACTION_NAME
from gui.prb_control.settings import FUNCTIONAL_INIT_RESULT

class HistoricalEntry(IPrbEntry):

    def makeDefCtx(self):
        return pre_queue_ctx.JoinModeCtx(QUEUE_TYPE.HISTORICAL)

    def create(self, ctx, callback = None):
        raise Exception, 'HistoricalIntro is not create entity'

    def join(self, ctx, callback = None):
        result = True
        if not isinstance(ctx, pre_queue_ctx.JoinModeCtx):
            result = False
            LOG_ERROR('Invalid context to join historical mode', ctx)
        else:
            g_prbCtrlEvents.onPreQueueFunctionalCreated(QUEUE_TYPE.HISTORICAL, False, None)
        if callback:
            callback(result)
        return

    def select(self, ctx, callback = None):
        self.join(ctx, callback=callback)


class HistoricalQueueFunctional(PreQueueFunctional, IStatefulFunctional):

    def __init__(self, settings = None):
        super(HistoricalQueueFunctional, self).__init__(QUEUE_TYPE.HISTORICAL, {QUEUE_EVENT_TYPE.ENQUEUED: g_playerEvents.onEnqueuedHistorical,
         QUEUE_EVENT_TYPE.DEQUEUED: g_playerEvents.onDequeuedHistorical,
         QUEUE_EVENT_TYPE.ENQUEUE_ERROR: g_playerEvents.onEnqueueHistoricalFailure,
         QUEUE_EVENT_TYPE.KICKED_FROM_QUEUE: g_playerEvents.onKickedFromHistoricalQueue,
         QUEUE_EVENT_TYPE.KICKED_FROM_ARENA: g_playerEvents.onKickedFromArena}, settings=settings)
        self.__requestCtx = PrbCtrlRequestCtx()

    def init(self, ctx = None):
        result = super(HistoricalQueueFunctional, self).init(ctx=ctx)
        g_eventDispatcher.loadHistoryBattles()
        g_eventsCache.onSyncCompleted += self.onEventsCacheResync
        g_eventBus.addListener(events.ChannelCarouselEvent.CAROUSEL_INITED, self.__handleCarouselInited, scope=EVENT_BUS_SCOPE.LOBBY)
        g_gameCtrl.captcha.onCaptchaInputCanceled += self.onCaptchaInputCanceled
        result = FUNCTIONAL_INIT_RESULT.addIfNot(result, FUNCTIONAL_INIT_RESULT.LOAD_WINDOW)
        return result

    def fini(self, woEvents = False):
        self.__requestCtx = None
        if not woEvents:
            g_eventDispatcher.unloadHistoryBattles()
        else:
            g_eventDispatcher.removeHistoryBattlesFromCarousel()
        g_gameCtrl.captcha.onCaptchaInputCanceled -= self.onCaptchaInputCanceled
        g_eventBus.removeListener(events.ChannelCarouselEvent.CAROUSEL_INITED, self.__handleCarouselInited, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventDispatcher.unloadHistoryBattles()
        g_eventsCache.onSyncCompleted -= self.onEventsCacheResync
        g_currentVehicle.setHistoricalBattle(None)
        super(HistoricalQueueFunctional, self).fini(woEvents=woEvents)
        return

    def getStates(self):
        return ({'isInHistoricalQueue': True}, dict(self._settings))

    def isInQueue(self):
        return isInHistoricalQueue()

    def showGUI(self):
        g_eventDispatcher.loadHistoryBattles()

    @process
    def doLeaveAction(self, dispatcher, ctx = None, showConfirmation = True):
        meta = self.getConfirmDialogMeta()
        if meta is not None:
            isConfirmed = yield DialogsInterface.showDialog(meta)
        else:
            isConfirmed = yield lambda callback: callback(True)
        if isConfirmed:
            super(HistoricalQueueFunctional, self).doLeaveAction(dispatcher, ctx=None)
        return

    def join(self, ctx, callback = None):
        if self.__requestCtx.isProcessing():
            LOG_ERROR('Request is processing', self.__requestCtx)
            if callback:
                callback(False)
            return
        if isParentControlActivated():
            g_eventDispatcher.showParentControlNotification()
            if callback:
                callback(False)
            return
        if not hasattr(BigWorld.player(), 'enqueueHistorical'):
            if callback:
                callback(False)
            LOG_ERROR('Player can not join to history queue')
            return
        self.__requestCtx = ctx
        self.__requestCtx.startProcessing(callback)
        invID = ctx.getVehicleInventoryID()
        histBattleID = ctx.getHistBattleID()
        isCreditsAmmo = ctx.getIsCreditsAmmo()
        BigWorld.player().enqueueHistorical(invID, histBattleID=histBattleID, isCreditsAmmo=isCreditsAmmo)
        LOG_DEBUG('Player is joining to historical queue', ctx)

    def leave(self, ctx, callback = None):
        if self.__requestCtx.isProcessing():
            LOG_ERROR('Request is processing', self.__requestCtx)
            if callback:
                callback(False)
            return
        if hasattr(BigWorld.player(), 'dequeueHistorical'):
            if self.isInQueue():
                self.__requestCtx = ctx
                self.__requestCtx.startProcessing(callback)
                BigWorld.player().dequeueHistorical()
            else:
                super(HistoricalQueueFunctional, self).leave(ctx, callback)
        else:
            if callback:
                callback(False)
            LOG_ERROR('Player can not exit from random queue')

    def getItemData(self):
        battleID = self.getSetting(PREQUEUE_SETTING_NAME.BATTLE_ID)
        return g_eventsCache.getHistoricalBattles().get(battleID)

    def canPlayerDoAction(self):
        histBattleID = self.getSetting(PREQUEUE_SETTING_NAME.BATTLE_ID)
        vehicleID = g_currentVehicle.item.intCD if g_currentVehicle.isPresent() else None
        historicalBattle = g_eventsCache.getHistoricalBattles().get(histBattleID)
        priceIndex, _ = self.getSelectedPrice(histBattleID, vehicleID)
        if historicalBattle is not None and vehicleID is not None:
            if historicalBattle.isFuture():
                return (False, '')
            if not historicalBattle.canParticipateWith(vehicleID):
                return (False, '')
            prices = historicalBattle.getShellsLayoutPrice(vehicleID)
            selected = priceIndex if priceIndex is not None else len(prices) - 1
            enoughGold, enoughCredits = historicalBattle.getShellsLayoutPriceStatus(vehicleID)[selected]
            if not enoughGold or not enoughCredits:
                return (False, '')
            return super(HistoricalQueueFunctional, self).canPlayerDoAction()
        else:
            return (False, '')

    def doAction(self, action = None, dispatcher = None):
        result = False
        if not self.isInQueue():
            histBattleID = self.getSetting(PREQUEUE_SETTING_NAME.BATTLE_ID)
            selectedVehicleID = self.getSetting(PREQUEUE_SETTING_NAME.SELECTED_VEHICLE_ID)
            _, isCreditsAmmo = self.getSelectedPrice(histBattleID, selectedVehicleID)
            self.join(pre_queue_ctx.JoinHistoricalQueueCtx(histBattleID, isCreditsAmmo, waitingID='prebattle/join'))
        else:
            self.leave(pre_queue_ctx.LeavePreQueueCtx(waitingID='prebattle/leave'))
        return result

    def doSelectAction(self, action):
        result = False
        if action.actionName == PREBATTLE_ACTION_NAME.HISTORICAL:
            g_eventDispatcher.showHistoryBattlesWindow()
            result = True
        return result

    def onEnqueued(self, *args):
        super(HistoricalQueueFunctional, self).onEnqueued(*args)
        self.__requestCtx.stopProcessing(True)
        g_eventDispatcher.loadBattleQueue()
        g_eventDispatcher.updateUI()

    def onDequeued(self, *args):
        super(HistoricalQueueFunctional, self).onDequeued(*args)
        self.__requestCtx.stopProcessing(True)
        g_eventDispatcher.loadHangar()
        g_eventDispatcher.updateUI()
        self.showGUI()
        self.__checkAvailability()

    def onEnqueueError(self, errorCode, _):
        super(HistoricalQueueFunctional, self).onEnqueueError(errorCode, _)
        self.__requestCtx.stopProcessing(False)
        SystemMessages.pushMessage(messages.getJoinFailureMessage(errorCode), type=SystemMessages.SM_TYPE.Error)

    def onKickedFromQueue(self, *args):
        super(HistoricalQueueFunctional, self).onKickedFromQueue(*args)
        self.__requestCtx.stopProcessing(True)
        g_eventDispatcher.loadHangar()
        g_eventDispatcher.updateUI()
        SystemMessages.pushMessage(messages.getKickReasonMessage('timeout'), type=SystemMessages.SM_TYPE.Warning)
        self.__checkAvailability()

    def onKickedFromArena(self, *args):
        super(HistoricalQueueFunctional, self).onKickedFromQueue(*args)
        self.__requestCtx.stopProcessing(True)
        g_eventDispatcher.loadHangar()
        g_eventDispatcher.updateUI()
        self.__checkAvailability()

    def onCaptchaInputCanceled(self):
        self.__requestCtx.stopProcessing(True)

    def getSelectedPrice(self, histBattleID, selectedVehicleID):
        return self.getSetting(PREQUEUE_SETTING_NAME.PRICE_INDEX, {}).get(histBattleID, {}).get(selectedVehicleID, (None, True))

    def onEventsCacheResync(self):
        if isInHistoricalQueue():
            return
        self.__checkAvailability()

    def _applySettings(self, settings):
        if PREQUEUE_SETTING_NAME.BATTLE_ID in settings:
            historicalBattle = g_eventsCache.getHistoricalBattles().get(settings[PREQUEUE_SETTING_NAME.BATTLE_ID])
            g_currentVehicle.setHistoricalBattle(historicalBattle)

    def __handleCarouselInited(self, _):
        g_eventDispatcher.addHistoryBattlesToCarousel()

    def __checkAvailability(self):
        if not g_eventsCache.getHistoricalBattles():
            LOG_DEBUG('No historical battles available.')
            self.leave(pre_queue_ctx.LeavePreQueueCtx(waitingID='prebattle/leave'))
            return
        else:
            historicalBattle = g_eventsCache.getHistoricalBattles().get(self._settings[PREQUEUE_SETTING_NAME.BATTLE_ID])
            if historicalBattle is None:
                LOG_DEBUG('Currently selected historical battle is no longer available.')
                self.leave(pre_queue_ctx.LeavePreQueueCtx(waitingID='prebattle/leave'))
            else:
                g_currentVehicle.setHistoricalBattle(historicalBattle)
            return
