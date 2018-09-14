# Embedded file name: scripts/client/gui/prb_control/functional/battle_tutorial.py
import BigWorld
from PlayerEvents import g_playerEvents
from constants import QUEUE_TYPE
from gui.prb_control import prb_getters
from gui.prb_control.context import pre_queue_ctx
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.functional import prequeue
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME

class TutorialPreQueueEntry(prequeue.PreQueueEntry):

    def __init__(self):
        super(TutorialPreQueueEntry, self).__init__(QUEUE_TYPE.TUTORIAL, FUNCTIONAL_FLAG.UNDEFINED)


class _TutorialQueueEventsSubscriber(prequeue.PlayersEventsSubscriber):

    def subscribe(self, functional):
        g_playerEvents.onTutorialEnqueued += functional.onEnqueued
        g_playerEvents.onTutorialDequeued += functional.onDequeued
        g_playerEvents.onTutorialEnqueueFailure += functional.onEnqueueError
        g_playerEvents.onKickedFromTutorialQueue += functional.onKickedFromQueue
        g_playerEvents.onKickedFromArena += functional.onKickedFromArena

    def unsubscribe(self, functional):
        g_playerEvents.onTutorialEnqueued -= functional.onEnqueued
        g_playerEvents.onTutorialDequeued -= functional.onDequeued
        g_playerEvents.onTutorialEnqueueFailure -= functional.onEnqueueError
        g_playerEvents.onKickedFromTutorialQueue -= functional.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= functional.onKickedFromArena


class TutorialQueueFunctional(prequeue.AccountQueueFunctional):

    def __init__(self):
        super(TutorialQueueFunctional, self).__init__(QUEUE_TYPE.TUTORIAL, _TutorialQueueEventsSubscriber(), FUNCTIONAL_FLAG.BATTLE_TUTORIAL)

    def init(self, ctx = None):
        g_eventDispatcher.startOffbattleTutorial()
        return super(TutorialQueueFunctional, self).init(ctx)

    def isInQueue(self):
        return prb_getters.isInTutorialQueue()

    def doSelectAction(self, action):
        if action.actionName == PREBATTLE_ACTION_NAME.BATTLE_TUTORIAL:
            g_eventDispatcher.startOffbattleTutorial()
            result = SelectResult(True, None)
        else:
            result = SelectResult(False, None)
        return result

    def onEnqueueError(self, *args):
        super(TutorialQueueFunctional, self).onEnqueueError(*args)
        g_prbCtrlEvents.onPreQueueFunctionalDestroyed()

    def onKickedFromQueue(self, *args):
        super(TutorialQueueFunctional, self).onKickedFromQueue(*args)
        g_prbCtrlEvents.onPreQueueFunctionalDestroyed()

    def onKickedFromArena(self, *args):
        super(TutorialQueueFunctional, self).onKickedFromArena(*args)
        g_prbCtrlEvents.onPreQueueFunctionalDestroyed()

    def _doQueue(self, ctx):
        BigWorld.player().enqueueTutorial()

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueTutorial()

    def _makeQueueCtxByAction(self, action = None):
        return pre_queue_ctx.QueueCtx()

    def _validateParentControl(self):
        return False
