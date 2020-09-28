# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/pre_queue/entity.py
import BigWorld
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG
from helpers import dependency
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntryPoint, PreQueueEntity
from gui.prb_control.entities.event.pre_queue.ctx import EventBattleQueueCtx
from gui.prb_control.entities.event.pre_queue.vehicles_watcher import EventBattlesVehiclesWatcher
from gui.prb_control.entities.event.pre_queue.actions_validator import EventBattleActionsValidator
from gui.prb_control.items import SelectResult, ValidationResult
from gui.prb_control.prb_getters import isInEventBattlesQueue
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, UNIT_RESTRICTION, SELECTOR_BATTLE_TYPES
from gui.prb_control.storages import prequeue_storage_getter
from gui.prb_control.entities.event.pre_queue.scheduler import EventScheduler
from gui.shared.utils.SelectorBattleTypesUtils import setBattleTypeAsKnown
from gui.wt_event.wt_event_helpers import hasEnoughTickets, isBossVehicle, isSpecialBossVehicle
from soft_exception import SoftException
from skeletons.gui.game_control import IGameEventController

class EventBattleSubscriber(PreQueueSubscriber):

    def subscribe(self, entity):
        g_playerEvents.onEnqueuedEventBattles += entity.onEnqueued
        g_playerEvents.onDequeuedEventBattles += entity.onDequeued
        g_playerEvents.onEnqueueEventBattlesFailure += entity.onEnqueueError
        g_playerEvents.onKickedFromEventBattles += entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena += entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure += entity.onArenaJoinFailure

    def unsubscribe(self, entity):
        g_playerEvents.onEnqueuedEventBattles -= entity.onEnqueued
        g_playerEvents.onDequeuedEventBattles -= entity.onDequeued
        g_playerEvents.onEnqueueEventBattlesFailure -= entity.onEnqueueError
        g_playerEvents.onKickedFromEventBattles -= entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure -= entity.onArenaJoinFailure


class EventBattleEntryPoint(PreQueueEntryPoint):

    def __init__(self):
        super(EventBattleEntryPoint, self).__init__(FUNCTIONAL_FLAG.EVENT | FUNCTIONAL_FLAG.LOAD_PAGE, QUEUE_TYPE.EVENT_BATTLES)

    def select(self, ctx, callback=None):
        super(EventBattleEntryPoint, self).select(ctx, callback)
        setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.EVENT_BATTLE)


class EventBattleEntity(PreQueueEntity):
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        super(EventBattleEntity, self).__init__(FUNCTIONAL_FLAG.EVENT, QUEUE_TYPE.EVENT_BATTLES, EventBattleSubscriber())
        self.__watcher = None
        self.reloadWT = False
        return

    @prequeue_storage_getter(QUEUE_TYPE.EVENT_BATTLES)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = EventBattlesVehiclesWatcher()
        self.__watcher.start()
        return super(EventBattleEntity, self).init(ctx=ctx)

    def fini(self, ctx=None, woEvents=False):
        if not woEvents:
            if not self.canSwitch(ctx):
                g_eventDispatcher.loadHangar()
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        return super(EventBattleEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def doSelectAction(self, action):
        return SelectResult(True) if action.actionName == PREBATTLE_ACTION_NAME.EVENT_BATTLE else super(EventBattleEntity, self).doSelectAction(action)

    def isInQueue(self):
        return isInEventBattlesQueue()

    def leave(self, ctx, callback=None):
        self.storage.suspend()
        super(EventBattleEntity, self).leave(ctx, callback=callback)

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        if not invID:
            raise SoftException('Inventory ID of vehicle can not be zero')
        return EventBattleQueueCtx(vehInvIDs=[1, invID], waitingID='prebattle/join')

    def _doQueue(self, ctx):
        BigWorld.player().enqueueEventBattles(ctx.getVehicleInventoryIDs())
        LOG_DEBUG('Sends request on queuing to the event battles', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueEventBattles()
        LOG_DEBUG('Sends request on dequeuing from the event battles')

    def _goToQueueUI(self):
        g_eventDispatcher.loadEventBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        if not self.reloadWT:
            g_eventDispatcher.loadHangar()
        else:
            self.reloadWT = False
            self.gameEventController.runEventQueue()

    def canPlayerDoAction(self):
        vehicle = g_currentVehicle.item
        if vehicle is not None:
            if not vehicle.isEvent:
                return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_NOT_VALID_FOR_EVENT)
            if isBossVehicle(vehicle) and not hasEnoughTickets() and not isSpecialBossVehicle(vehicle):
                return ValidationResult(False, UNIT_RESTRICTION.EVENT_TICKETS_SHORTAGE)
        return super(EventBattleEntity, self).canPlayerDoAction()

    def _createActionsValidator(self):
        return EventBattleActionsValidator(self)

    def _createScheduler(self):
        return EventScheduler(self)
