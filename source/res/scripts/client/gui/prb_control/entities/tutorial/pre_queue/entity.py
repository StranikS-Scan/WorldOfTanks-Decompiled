# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/tutorial/pre_queue/entity.py
import BigWorld
from PlayerEvents import g_playerEvents
from constants import QUEUE_TYPE
from gui.prb_control import prb_getters
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.pre_queue.ctx import QueueCtx
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntryPoint, PreQueueEntity
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME

class TutorialSubscriber(PreQueueSubscriber):
    """
    Tutorial events subscriber
    """

    def subscribe(self, entity):
        g_playerEvents.onTutorialEnqueued += entity.onEnqueued
        g_playerEvents.onTutorialDequeued += entity.onDequeued
        g_playerEvents.onTutorialEnqueueFailure += entity.onEnqueueError
        g_playerEvents.onKickedFromTutorialQueue += entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena += entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure += entity.onArenaJoinFailure

    def unsubscribe(self, entity):
        g_playerEvents.onTutorialEnqueued -= entity.onEnqueued
        g_playerEvents.onTutorialDequeued -= entity.onDequeued
        g_playerEvents.onTutorialEnqueueFailure -= entity.onEnqueueError
        g_playerEvents.onKickedFromTutorialQueue -= entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure -= entity.onArenaJoinFailure


class TutorialEntryPoint(PreQueueEntryPoint):
    """
    Tutorial entry point
    """

    def __init__(self):
        super(TutorialEntryPoint, self).__init__(FUNCTIONAL_FLAG.TUTORIAL, QUEUE_TYPE.TUTORIAL)


class TutorialEntity(PreQueueEntity):
    """
    Tutorial entity class
    """

    def __init__(self):
        super(TutorialEntity, self).__init__(FUNCTIONAL_FLAG.TUTORIAL, QUEUE_TYPE.TUTORIAL, TutorialSubscriber())

    def init(self, ctx=None):
        result = super(TutorialEntity, self).init(ctx)
        g_eventDispatcher.loadHangar()
        g_eventDispatcher.startOffbattleTutorial()
        return result

    def isInQueue(self):
        return prb_getters.isInTutorialQueue()

    def doSelectAction(self, action):
        return SelectResult(True) if action.actionName == PREBATTLE_ACTION_NAME.BATTLE_TUTORIAL else super(TutorialEntity, self).doSelectAction(action)

    def onEnqueueError(self, *args):
        super(TutorialEntity, self).onEnqueueError(*args)
        g_prbCtrlEvents.onPreQueueLeft()

    def onKickedFromQueue(self, *args):
        super(TutorialEntity, self).onKickedFromQueue(*args)
        g_prbCtrlEvents.onPreQueueLeft()

    def onKickedFromArena(self, *args):
        super(TutorialEntity, self).onKickedFromArena(*args)
        g_prbCtrlEvents.onPreQueueLeft()

    def onArenaJoinFailure(self, *args):
        super(TutorialEntity, self).onKickedFromArena(*args)
        g_prbCtrlEvents.onPreQueueLeft()

    def _doQueue(self, ctx):
        BigWorld.player().enqueueTutorial()

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueTutorial()

    def _makeQueueCtxByAction(self, action=None):
        return QueueCtx()

    def _validateParentControl(self):
        return False
