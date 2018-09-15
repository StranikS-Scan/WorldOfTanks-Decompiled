# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event_two/pre_queue/entity.py
import BigWorld
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from constants import QUEUE_TYPE, PREBATTLE_TYPE
from debug_utils import LOG_WARNING, LOG_ERROR, LOG_DEBUG
from gui.Scaleform.daapi.view.dialogs import rally_dialog_meta
from gui.prb_control import prb_getters
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.event_two.pre_queue.actions_validator import EventBattlesTwoActionsValidator
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.entities.base.pre_queue.ctx import DequeueCtx
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntryPoint, PreQueueEntity
from gui.prb_control.entities.event_two.pre_queue.ctx import EventBattlesTwoQueueCtx
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.prb_control.storages import prequeue_storage_getter
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

class EventBattlesTwoSubscriber(PreQueueSubscriber):
    """
    EventBattlesTwo event subscriber
    """

    def subscribe(self, entity):
        g_playerEvents.onEnqueuedEventBattlesTwo += entity.onEnqueued
        g_playerEvents.onDequeuedEventBattlesTwo += entity.onDequeued
        g_playerEvents.onEnqueuedEventBattlesTwoFailure += entity.onEnqueueError
        g_playerEvents.onKickedFromEventBattlesTwoQueue += entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena += entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure += entity.onArenaJoinFailure

    def unsubscribe(self, entity):
        g_playerEvents.onEnqueuedEventBattlesTwo -= entity.onEnqueued
        g_playerEvents.onDequeuedEventBattlesTwo -= entity.onDequeued
        g_playerEvents.onEnqueuedEventBattlesTwoFailure -= entity.onEnqueueError
        g_playerEvents.onKickedFromEventBattlesTwoQueue -= entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure -= entity.onArenaJoinFailure


class EventBattlesTwoEntryPoint(PreQueueEntryPoint):
    """
    EventBattlesTwo entry point
    """

    def __init__(self):
        super(EventBattlesTwoEntryPoint, self).__init__(FUNCTIONAL_FLAG.EVENT_BATTLES_2, QUEUE_TYPE.EVENT_BATTLES_2)


class EventBattlesTwoEntity(PreQueueEntity):
    """
    EventBattlesTwo entity
    """

    def __init__(self):
        super(EventBattlesTwoEntity, self).__init__(FUNCTIONAL_FLAG.EVENT_BATTLES_2, QUEUE_TYPE.EVENT_BATTLES_2, EventBattlesTwoSubscriber())

    @vehicleAmmoCheck
    def queue(self, ctx, callback=None):
        super(EventBattlesTwoEntity, self).queue(ctx, callback=callback)

    def isInQueue(self):
        return prb_getters.isInEventBattlesTwoQueue()

    def _createActionsValidator(self):
        return EventBattlesTwoActionsValidator(self)

    def _doQueue(self, ctx):
        BigWorld.player().enqueueEventBattlesTwo(ctx.getVehicleInventoryID())
        LOG_DEBUG('Sends request on queuing to the EventBattlesTwo battle', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueEventBattlesTwo()
        LOG_DEBUG('Sends request on dequeuing from the EventBattlesTwo battle', ctx)

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        assert invID, 'Inventory ID of vehicle can not be zero'
        return EventBattlesTwoQueueCtx(invID, waitingID='prebattle/join')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()
