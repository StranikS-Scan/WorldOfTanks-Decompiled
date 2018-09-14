# Embedded file name: scripts/client/gui/prb_control/functional/prequeue.py
from constants import QUEUE_TYPE
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui import SystemMessages
from gui.Scaleform.daapi.view.dialogs import rally_dialog_meta
from gui.game_control import g_instance as g_gameCtrl
from gui.prb_control import prb_getters
from gui.prb_control.context import PrbCtrlRequestCtx, pre_queue_ctx
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.formatters import messages
from gui.prb_control.functional import interfaces
from gui.prb_control.restrictions.permissions import PreQueuePermissions
from gui.prb_control.settings import FUNCTIONAL_FLAG, CTRL_ENTITY_TYPE
from gui.prb_control.settings import REQUEST_TYPE
from gui.shared.utils.ListenersCollection import ListenersCollection
from helpers import isPlayerAccount
__all__ = ('PreQueueEntry', 'PlayersEventsSubscriber', 'NoPreQueueFunctional', 'AccountQueueFunctional')

class PreQueueEntry(interfaces.IPrbEntry):

    def __init__(self, queueType, flags):
        super(PreQueueEntry, self).__init__()
        raise queueType in QUEUE_TYPE.ALL or AssertionError
        self.__queueType = queueType
        self.__flags = flags

    def makeDefCtx(self):
        return pre_queue_ctx.JoinModeCtx(self.__queueType, flags=self.__flags)

    def create(self, ctx, callback = None):
        raise Exception('QueueEntry is not create entity')

    def join(self, ctx, callback = None):
        result = True
        if not isinstance(ctx, pre_queue_ctx.JoinModeCtx):
            result = False
            LOG_ERROR('Invalid context to join queue mode', ctx)
        else:
            self._goToFunctional()
        if callback is not None:
            callback(result)
        return

    def select(self, ctx, callback = None):
        self.join(ctx, callback=callback)

    def _goToFunctional(self):
        g_prbCtrlEvents.onPreQueueFunctionalCreated(self.__queueType)


class PlayersEventsSubscriber(object):
    __slots__ = ()

    def subscribe(self, functional):
        raise NotImplementedError

    def unsubscribe(self, functional):
        raise NotImplementedError


class NoPreQueueFunctional(interfaces.IPreQueueFunctional):

    def getFunctionalFlags(self):
        return FUNCTIONAL_FLAG.NO_QUEUE

    def canPlayerDoAction(self):
        return (True, '')


class PreQueueFunctional(ListenersCollection, interfaces.IPreQueueFunctional):

    def __init__(self, queueType, subscriber, flags = FUNCTIONAL_FLAG.UNDEFINED):
        super(PreQueueFunctional, self).__init__()
        self._queueType = queueType
        self._subscriber = subscriber
        self._setListenerClass(interfaces.IPreQueueListener)
        self._hasEntity = False
        self._flags = flags | FUNCTIONAL_FLAG.PRE_QUEUE
        g_prbCtrlEvents.onPreQueueFunctionalChanged()

    def init(self, ctx = None):
        self._hasEntity = True
        self._subscriber.subscribe(self)
        self._invokeListeners('onPreQueueFunctionalInited')
        result = FUNCTIONAL_FLAG.UNDEFINED
        if self.isInQueue():
            result |= self._goToQueueUI()
        return result

    def fini(self, woEvents = False):
        self._hasEntity = False
        if isPlayerAccount():
            for listener in self._listeners:
                listener.onPreQueueFunctionalFinished()

        self._setListenerClass(None)
        self._subscriber.unsubscribe(self)
        return

    def getFunctionalFlags(self):
        return self._flags

    def setFunctionalFlags(self, flag):
        self._flags = flag

    def hasLockedState(self):
        return self.isInQueue()

    def getEntityType(self):
        return self._queueType

    def getPermissions(self, pID = None, **kwargs):
        raise pID is None or AssertionError('Current player has no any player in that mode')
        return PreQueuePermissions(self.isInQueue())

    def getConfirmDialogMeta(self, ctx):
        meta = None
        if self.hasLockedState():
            meta = rally_dialog_meta.RallyLeaveDisabledDialogMeta(CTRL_ENTITY_TYPE.PREQUEUE, self._queueType)
        return meta

    def canPlayerDoAction(self):
        return (not self.isInQueue(), '')

    def showGUI(self, ctx = None):
        self._goToQueueUI()

    def exitFromQueue(self):
        self.doAction()

    def hasEntity(self):
        return self._hasEntity

    def request(self, ctx, callback = None):
        requestType = ctx.getRequestType()
        if requestType == REQUEST_TYPE.QUEUE:
            self.queue(ctx, callback=callback)
        elif requestType == REQUEST_TYPE.DEQUEUE:
            self.dequeue(ctx, callback=callback)
        else:
            LOG_ERROR('PreQueueFunctional supports QUEUE and DEQUEUE requests only', ctx)
            if callback is not None:
                callback(False)
        return

    def queue(self, ctx, callback = None):
        if callback is not None:
            callback(False)
        return

    def dequeue(self, ctx, callback = None):
        if callback is not None:
            callback(False)
        return

    def leave(self, ctx, callback = None):

        def __leave(_ = True):
            g_prbCtrlEvents.onPreQueueFunctionalDestroyed()
            if callback is not None:
                callback(True)
            return

        if self.isInQueue():
            self.dequeue(pre_queue_ctx.DequeueCtx(waitingID='prebattle/leave'), callback=__leave)
        else:
            __leave()

    def onEnqueued(self, *args):
        self._invokeListeners('onEnqueued', self._queueType, *args)
        self._goToQueueUI()

    def onDequeued(self, *args):
        self._invokeListeners('onDequeued', self._queueType, *args)
        self._exitFromQueueUI()

    def onEnqueueError(self, errorCode, *args):
        self._invokeListeners('onEnqueueError', self._queueType, *args)
        self._exitFromQueueUI()
        SystemMessages.pushMessage(messages.getJoinFailureMessage(errorCode), type=SystemMessages.SM_TYPE.Error)

    def onKickedFromQueue(self, *args):
        self._invokeListeners('onKickedFromQueue', self._queueType, *args)
        self._exitFromQueueUI()
        SystemMessages.pushMessage(messages.getKickReasonMessage('timeout'), type=SystemMessages.SM_TYPE.Warning)

    def onKickedFromArena(self, *args):
        self._invokeListeners('onKickedFromArena', self._queueType, *args)
        self._exitFromQueueUI()

    def _goToQueueUI(self):
        return FUNCTIONAL_FLAG.UNDEFINED

    def _exitFromQueueUI(self):
        pass


class AccountQueueFunctional(PreQueueFunctional):

    def __init__(self, queueType, subscriber, flags = FUNCTIONAL_FLAG.UNDEFINED):
        super(AccountQueueFunctional, self).__init__(queueType, subscriber, flags)
        self._requestCtx = PrbCtrlRequestCtx()

    def init(self, ctx = None):
        g_gameCtrl.captcha.onCaptchaInputCanceled += self.__onCaptchaInputCanceled
        return super(AccountQueueFunctional, self).init(ctx)

    def fini(self, woEvents = False):
        self._requestCtx.clear()
        g_gameCtrl.captcha.onCaptchaInputCanceled -= self.__onCaptchaInputCanceled
        super(AccountQueueFunctional, self).fini(woEvents)

    def doAction(self, action = None):
        if not self.isInQueue():
            self.queue(self._makeQueueCtxByAction(action))
        else:
            self.dequeue(pre_queue_ctx.DequeueCtx(waitingID='prebattle/leave'))
        return True

    def queue(self, ctx, callback = None):
        if ctx is None:
            ctx = self._makeQueueCtxByAction()
        if self._requestCtx.isProcessing():
            LOG_ERROR('Request is processing', self._requestCtx)
            if callback is not None:
                callback(False)
            return
        elif self.isInQueue():
            LOG_ERROR('Player already is in the queue', self._requestCtx)
            if callback is not None:
                callback(False)
            return
        elif self._validateParentControl():
            if callback is not None:
                callback(False)
            return
        else:
            self._requestCtx = ctx
            self._requestCtx.startProcessing(callback)
            try:
                self._doQueue(ctx)
            except (AttributeError, TypeError, NotImplementedError):
                LOG_CURRENT_EXCEPTION()
                self._requestCtx.stopProcessing(False)

            return

    def dequeue(self, ctx, callback = None):
        if self._requestCtx.isProcessing():
            LOG_ERROR('Request is processing', self._requestCtx)
            if callback:
                callback(False)
            return
        elif not self.isInQueue():
            LOG_ERROR('Player is not in the queue', ctx)
            if callback is not None:
                callback(False)
            return
        else:
            self._requestCtx = ctx
            self._requestCtx.startProcessing(callback)
            try:
                self._doDequeue(ctx)
            except (AttributeError, TypeError, NotImplementedError):
                LOG_CURRENT_EXCEPTION()
                self._requestCtx.stopProcessing(False)

            return

    def onEnqueued(self, *args):
        self._requestCtx.stopProcessing(True)
        super(AccountQueueFunctional, self).onEnqueued(*args)

    def onDequeued(self, *args):
        self._requestCtx.stopProcessing(True)
        super(AccountQueueFunctional, self).onDequeued(*args)

    def onEnqueueError(self, *args):
        self._requestCtx.stopProcessing(False)
        super(AccountQueueFunctional, self).onEnqueueError(*args)

    def onKickedFromQueue(self, *args):
        self._requestCtx.stopProcessing(True)
        super(AccountQueueFunctional, self).onKickedFromQueue(*args)

    def onKickedFromArena(self, *args):
        self._requestCtx.stopProcessing(True)
        super(AccountQueueFunctional, self).onKickedFromArena(*args)

    def _doQueue(self, ctx):
        raise NotImplementedError('Routine _doQueue must be overridden')

    def _doDequeue(self, ctx):
        raise NotImplementedError('Routine _doDequeue must be overridden')

    def _makeQueueCtxByAction(self, action = None):
        raise NotImplementedError('Routine _makeDefQueueCtx must be overridden')

    def _validateParentControl(self):
        result = prb_getters.isParentControlActivated()
        if result:
            g_eventDispatcher.showParentControlNotification()
        return result

    def __onCaptchaInputCanceled(self):
        self._requestCtx.stopProcessing(False)
