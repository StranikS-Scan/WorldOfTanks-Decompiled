# Embedded file name: scripts/client/gui/prb_control/functional/random_queue.py
import BigWorld
import ArenaType
from constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG, LOG_ERROR
from PlayerEvents import g_playerEvents
from gui import SystemMessages
from gui.game_control import g_instance as g_gameCtrl
from gui.prb_control import isParentControlActivated, isInRandomQueue
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.functional.decorators import vehicleAmmoCheck
from gui.prb_control.functional.default import PreQueueFunctional
from gui.prb_control.context import PrbCtrlRequestCtx, pre_queue_ctx
from gui.prb_control.formatters import messages
from gui.prb_control.settings import QUEUE_EVENT_TYPE, FUNCTIONAL_INIT_RESULT

class RandomQueueFunctional(PreQueueFunctional):

    def __init__(self, settings = None):
        super(RandomQueueFunctional, self).__init__(QUEUE_TYPE.RANDOMS, {QUEUE_EVENT_TYPE.ENQUEUED: g_playerEvents.onEnqueuedRandom,
         QUEUE_EVENT_TYPE.DEQUEUED: g_playerEvents.onDequeuedRandom,
         QUEUE_EVENT_TYPE.ENQUEUE_ERROR: g_playerEvents.onEnqueueRandomFailure,
         QUEUE_EVENT_TYPE.KICKED_FROM_QUEUE: g_playerEvents.onKickedFromRandomQueue,
         QUEUE_EVENT_TYPE.KICKED_FROM_ARENA: g_playerEvents.onKickedFromArena}, settings=settings)
        self.__requestCtx = PrbCtrlRequestCtx()

    def init(self, ctx = None):
        result = super(RandomQueueFunctional, self).init(ctx)
        g_gameCtrl.captcha.onCaptchaInputCanceled += self.onCaptchaInputCanceled
        if self.isInQueue():
            g_eventDispatcher.loadBattleQueue()
            result = FUNCTIONAL_INIT_RESULT.addIfNot(result, FUNCTIONAL_INIT_RESULT.LOAD_PAGE)
        return result

    def fini(self, woEvents = False):
        self.__requestCtx = None
        g_gameCtrl.captcha.onCaptchaInputCanceled -= self.onCaptchaInputCanceled
        super(RandomQueueFunctional, self).fini(woEvents)
        return

    @vehicleAmmoCheck
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
        if not hasattr(BigWorld.player(), 'enqueueRandom'):
            if callback:
                callback(False)
            LOG_ERROR('Player can not join to random queue')
            return
        mapID = ctx.getDemoArenaTypeID()
        if mapID:
            LOG_DEBUG('Demonstrator mapID:', ArenaType.g_cache[mapID].geometryName)
        self.__requestCtx = ctx
        self.__requestCtx.startProcessing(callback)
        BigWorld.player().enqueueRandom(ctx.getVehicleInventoryID(), gameplaysMask=ctx.getGamePlayMask(), arenaTypeID=mapID)
        LOG_DEBUG('Player is joining to random queue', ctx)

    def leave(self, ctx, callback = None):
        if self.__requestCtx.isProcessing():
            LOG_ERROR('Request is processing', self.__requestCtx)
            if callback:
                callback(False)
            return
        if hasattr(BigWorld.player(), 'dequeueRandom'):
            if self.isInQueue():
                self.__requestCtx = ctx
                self.__requestCtx.startProcessing(callback)
                BigWorld.player().dequeueRandom()
            else:
                super(RandomQueueFunctional, self).leave(ctx, callback)
        else:
            if callback:
                callback(False)
            LOG_ERROR('Player can not exit from random queue')

    def isInQueue(self):
        return isInRandomQueue()

    def hasGUIPage(self):
        return True

    def doAction(self, action = None, dispatcher = None):
        result = False

        def _leavePreQueue():
            self.leave(pre_queue_ctx.LeavePreQueueCtx(waitingID='prebattle/leave'))

        if not self.isInQueue():

            def _joinResponse(success):
                if not success:
                    _leavePreQueue()

            self.join(pre_queue_ctx.JoinRandomQueueCtx(action.mapID if action else 0, waitingID='prebattle/join'), callback=_joinResponse)
        else:
            _leavePreQueue()
        return result

    def onEnqueued(self):
        super(RandomQueueFunctional, self).onEnqueued()
        self.__requestCtx.stopProcessing(True)
        g_eventDispatcher.loadBattleQueue()
        g_eventDispatcher.updateUI()

    def onDequeued(self):
        super(RandomQueueFunctional, self).onDequeued()
        self.__requestCtx.stopProcessing(True)
        g_prbCtrlEvents.onPreQueueFunctionalDestroyed()
        g_eventDispatcher.loadHangar()

    def onEnqueueError(self, errorCode, _):
        super(RandomQueueFunctional, self).onEnqueueError(errorCode, _)
        self.__requestCtx.stopProcessing(False)
        g_prbCtrlEvents.onPreQueueFunctionalDestroyed()
        SystemMessages.pushMessage(messages.getJoinFailureMessage(errorCode), type=SystemMessages.SM_TYPE.Error)

    def onKickedFromQueue(self):
        super(RandomQueueFunctional, self).onKickedFromQueue()
        self.__requestCtx.stopProcessing(True)
        g_prbCtrlEvents.onPreQueueFunctionalDestroyed()
        g_eventDispatcher.loadHangar()
        g_eventDispatcher.updateUI()
        SystemMessages.pushMessage(messages.getKickReasonMessage('timeout'), type=SystemMessages.SM_TYPE.Warning)

    def onKickedFromArena(self, errorCode):
        super(RandomQueueFunctional, self).onKickedFromArena(errorCode)
        self.__requestCtx.stopProcessing(True)
        g_prbCtrlEvents.onPreQueueFunctionalDestroyed()
        g_eventDispatcher.loadHangar()
        g_eventDispatcher.updateUI()

    def onCaptchaInputCanceled(self):
        self.__requestCtx.stopProcessing(True)
        g_prbCtrlEvents.onPreQueueFunctionalDestroyed()
