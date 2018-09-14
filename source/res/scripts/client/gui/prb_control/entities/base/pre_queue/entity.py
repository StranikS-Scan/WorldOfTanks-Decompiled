# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/pre_queue/entity.py
from constants import QUEUE_TYPE
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_DEBUG
from gui import SystemMessages
from gui.Scaleform.daapi.view.dialogs import rally_dialog_meta
from gui.prb_control import prb_getters
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.formatters import messages
from gui.prb_control.entities.base.entity import BasePrbEntity, BasePrbEntryPoint
from gui.prb_control.entities.base.pre_queue.ctx import JoinPreQueueModeCtx, PrbCtrlRequestCtx, DequeueCtx
from gui.prb_control.entities.base.pre_queue.event_vehicle_extension import EventVehicleMeta
from gui.prb_control.entities.base.pre_queue.listener import IPreQueueListener
from gui.prb_control.entities.base.pre_queue.permissions import PreQueuePermissions
from gui.prb_control.settings import FUNCTIONAL_FLAG, CTRL_ENTITY_TYPE
from gui.prb_control.settings import REQUEST_TYPE
from gui.shared.utils.listeners_collection import ListenersCollection

class BasePreQueueEntity(BasePrbEntity):
    """
    Base class which describes entityity of pre queue.
    """

    def getCtrlType(self):
        return CTRL_ENTITY_TYPE.PREQUEUE

    def hasGUIPage(self):
        """
        Is prebattle has UI page.
        """
        return False

    def exitFromQueue(self):
        """
        Routine invokes when player is exiting from queue.
        """
        return False


class PreQueueSubscriber(object):
    """
    Base class for pre queue events subscription.
    """
    __slots__ = ()

    def subscribe(self, entity):
        """
        Do all the job about subscription.
        Args:
            entity: pre queue entity
        """
        raise NotImplementedError

    def unsubscribe(self, entity):
        """
        Do all the job about subscription.
        Args:
            entity: pre queue entity
        """
        raise NotImplementedError


class PreQueueEntryPoint(BasePrbEntryPoint):
    """
    Pre queue entry point class.
    """

    def __init__(self, modeFlags, queueType):
        super(PreQueueEntryPoint, self).__init__(entityFlags=FUNCTIONAL_FLAG.PRE_QUEUE, modeFlags=modeFlags)
        assert queueType in QUEUE_TYPE.ALL or queueType == QUEUE_TYPE.UNKNOWN
        self.__queueType = queueType

    def makeDefCtx(self):
        return JoinPreQueueModeCtx(self.__queueType, flags=self.getFunctionalFlags())

    def create(self, ctx, callback=None):
        raise Exception('QueueEntry is not create entity')

    def join(self, ctx, callback=None):
        result = True
        if not isinstance(ctx, JoinPreQueueModeCtx):
            result = False
            LOG_ERROR('Invalid context to join queue mode', ctx)
        else:
            self._goToEntity()
        if callback is not None:
            callback(result)
        return

    def select(self, ctx, callback=None):
        self.join(ctx, callback)

    def _goToEntity(self):
        """
        Method that actually joins us to an entity.
        """
        g_prbCtrlEvents.onPreQueueJoined(self.__queueType)


class PreQueueEntity(BasePreQueueEntity, ListenersCollection):
    """
    Pre queue entity class.
    """
    __metaclass__ = EventVehicleMeta

    def __init__(self, modeFlags, queueType, subscriber):
        super(PreQueueEntity, self).__init__(entityFlags=FUNCTIONAL_FLAG.PRE_QUEUE, modeFlags=modeFlags)
        self._queueType = queueType
        self._subscriber = subscriber
        self._setListenerClass(IPreQueueListener)
        self._requestCtx = PrbCtrlRequestCtx()

    def init(self, ctx=None):
        self._subscriber.subscribe(self)
        result = super(PreQueueEntity, self).init(ctx=ctx)
        if self.isInQueue():
            result |= self._goToQueueUI()
        return result

    def fini(self, ctx=None, woEvents=False):
        self.clear()
        self._subscriber.unsubscribe(self)
        if self._requestCtx.isProcessing:
            self._requestCtx.stopProcessing(True)
        self._requestCtx.clear()
        return super(PreQueueEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def getQueueType(self):
        return self._queueType

    def doAction(self, action=None):
        if not self.isInQueue():
            self.queue(self._makeQueueCtxByAction(action))
        else:
            self.dequeue(DequeueCtx(waitingID='prebattle/leave'))
        return True

    def hasLockedState(self):
        return self.isInQueue()

    def getEntityType(self):
        return self._queueType

    def getPermissions(self, pID=None, **kwargs):
        assert pID is None, 'Current player has no any player in that mode'
        return PreQueuePermissions(self.isInQueue())

    def getConfirmDialogMeta(self, ctx):
        meta = None
        if self.hasLockedState():
            meta = rally_dialog_meta.RallyLeaveDisabledDialogMeta(CTRL_ENTITY_TYPE.PREQUEUE, self._queueType)
        return meta

    def showGUI(self, ctx=None):
        self._goToQueueUI()

    def exitFromQueue(self):
        self.doAction()

    def request(self, ctx, callback=None):
        requestType = ctx.getRequestType()
        if requestType == REQUEST_TYPE.QUEUE:
            self.queue(ctx, callback=callback)
        elif requestType == REQUEST_TYPE.DEQUEUE:
            self.dequeue(ctx, callback=callback)
        else:
            LOG_ERROR('PreQueueEntity supports QUEUE and DEQUEUE requests only', ctx)
            if callback is not None:
                callback(False)
        return

    def queue(self, ctx, callback=None):
        """
        Sends request to enqueue.
        Args:
            ctx: queue context
            callback: operation callback
        """
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

    def dequeue(self, ctx, callback=None):
        """
        Sends request to dequeue.
        Args:
            ctx: dequeue context
            callback: operation callback
        """
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

    def leave(self, ctx, callback=None):

        def __leave(_=True):
            g_prbCtrlEvents.onPreQueueLeft()
            if callback is not None:
                callback(True)
            return

        if self.isInQueue():
            self.dequeue(DequeueCtx(waitingID='prebattle/leave'), callback=__leave)
        else:
            __leave()

    def onEnqueued(self, *args):
        """
        Routine must be invoked when player goes to queue.
        """
        self._requestCtx.stopProcessing(True)
        self._invokeListeners('onEnqueued', self._queueType, *args)
        self._goToQueueUI()

    def onDequeued(self, *args):
        """
        Routine must be invoked when player leaves queue.
        """
        self._requestCtx.stopProcessing(True)
        self._invokeListeners('onDequeued', self._queueType, *args)
        self._exitFromQueueUI()

    def onEnqueueError(self, errorCode, *args):
        """
        Routine must be invoked when player receives enqueue error.
        """
        self._requestCtx.stopProcessing(True)
        self._invokeListeners('onEnqueueError', self._queueType, *args)
        self._exitFromQueueUI()
        SystemMessages.pushMessage(messages.getJoinFailureMessage(errorCode), type=SystemMessages.SM_TYPE.Error)

    def onKickedFromQueue(self, *args):
        """
        Routine must be invoked when player is kicked from queue.
        """
        self._requestCtx.stopProcessing(True)
        self._invokeListeners('onKickedFromQueue', self._queueType, *args)
        self._exitFromQueueUI()
        SystemMessages.pushI18nMessage('#system_messages:arena_start_errors/prb/kick/timeout', type=SystemMessages.SM_TYPE.Warning)

    def onKickedFromArena(self, *args):
        """
        Routine must be invoked when player is kicked from arena.
        """
        self._requestCtx.stopProcessing(True)
        self._invokeListeners('onKickedFromArena', self._queueType, *args)
        self._exitFromQueueUI()

    def onArenaJoinFailure(self, *args):
        """
        Routine must be invoked when player received an error during arena join process.
        """
        self._invokeListeners('onArenaJoinFailure', self._queueType, *args)
        self._exitFromQueueUI()

    def _createActionsValidator(self):
        return PreQueueActionsValidator(self)

    def _goToQueueUI(self):
        """
        Routine that must be invoked when UI should show proper queue component.
        Returns:
            functional flag of UI load action
        """
        return FUNCTIONAL_FLAG.UNDEFINED

    def _exitFromQueueUI(self):
        """
        Routine that must be invoked when UI should hide proper queue component.
        """
        pass

    def _doQueue(self, ctx):
        """
        Method that should send player into queue at system level.
        Args:
            ctx: queue request context
        """
        raise NotImplementedError('Routine _doQueue must be overridden')

    def _doDequeue(self, ctx):
        """
        Method that should remove player from queue at system level.
        Args:
            ctx: dequeue request context
        """
        raise NotImplementedError('Routine _doDequeue must be overridden')

    def _makeQueueCtxByAction(self, action=None):
        """
        Build queue context by prebattle aciton
        Args:
            action: prebattle action
        
        Returns:
            queue context
        """
        raise NotImplementedError('Routine _makeDefQueueCtx must be overridden')

    def _validateParentControl(self):
        """
        Validates parent control restrictions.
        Returns:
            has pre queue any restrictions
        """
        result = prb_getters.isParentControlActivated()
        if result:
            g_eventDispatcher.showParentControlNotification()
        return result
