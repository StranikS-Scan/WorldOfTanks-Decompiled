# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/functional/fallout.py
import BigWorld
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.prb_control.context import pre_queue_ctx
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.functional import unit
from gui.prb_control.functional import prequeue
from gui.prb_control.functional.decorators import falloutQueueAmmoCheck
from gui.prb_control.functional.interfaces import IPrbEntry
from gui.prb_control.items import SelectResult
from gui.prb_control.prb_getters import isInFalloutClassic, isInFalloutMultiteam
from gui.prb_control.restrictions.permissions import FalloutQueuePermissions
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from gui.prb_control.settings import PREBATTLE_RESTRICTION
from gui.prb_control.storage import prequeue_storage_getter
from gui.shared.gui_items.Vehicle import Vehicle

class _FalloutEventsSubscriber(prequeue.PlayersEventsSubscriber):

    def subscribe(self, functional):
        pass

    def unsubscribe(self, functional):
        pass


class _FalloutClassicEventsSubscriber(_FalloutEventsSubscriber):

    def subscribe(self, functional):
        g_playerEvents.onEnqueuedFalloutClassic += functional.onEnqueued
        g_playerEvents.onDequeuedFalloutClassic += functional.onDequeued
        g_playerEvents.onEnqueueFalloutClassicFailure += functional.onEnqueueError
        g_playerEvents.onKickedFromFalloutClassic += functional.onKickedFromQueue
        g_playerEvents.onKickedFromArena += functional.onKickedFromArena

    def unsubscribe(self, functional):
        g_playerEvents.onEnqueuedFalloutClassic -= functional.onEnqueued
        g_playerEvents.onDequeuedFalloutClassic -= functional.onDequeued
        g_playerEvents.onEnqueueFalloutClassicFailure -= functional.onEnqueueError
        g_playerEvents.onKickedFromFalloutClassic -= functional.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= functional.onKickedFromArena


class _FalloutMultiTeamEventsSubscriber(_FalloutEventsSubscriber):

    def subscribe(self, functional):
        g_playerEvents.onEnqueuedFalloutMultiteam += functional.onEnqueued
        g_playerEvents.onDequeuedFalloutMultiteam += functional.onDequeued
        g_playerEvents.onEnqueueFalloutMultiteamFailure += functional.onEnqueueError
        g_playerEvents.onKickedFromFalloutMultiteam += functional.onKickedFromQueue
        g_playerEvents.onKickedFromArena += functional.onKickedFromArena

    def unsubscribe(self, functional):
        g_playerEvents.onEnqueuedFalloutMultiteam -= functional.onEnqueued
        g_playerEvents.onDequeuedFalloutMultiteam -= functional.onDequeued
        g_playerEvents.onEnqueueFalloutMultiteamFailure -= functional.onEnqueueError
        g_playerEvents.onKickedFromFalloutMultiteam -= functional.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= functional.onKickedFromArena


class NoFalloutEntry(IPrbEntry):

    def __init__(self, queueType, flags):
        super(NoFalloutEntry, self).__init__()
        self.__queueType = queueType
        self.__flags = flags

    def makeDefCtx(self):
        return pre_queue_ctx.JoinModeCtx(self.__queueType, flags=self.__flags)

    def create(self, ctx, callback=None):
        raise Exception('QueueEntry is not create entity')

    def join(self, ctx, callback=None):
        result = True
        if not isinstance(ctx, pre_queue_ctx.JoinModeCtx):
            result = False
            LOG_ERROR('Invalid context to join queue mode', ctx)
        else:
            self._goToFunctional()
        if callback is not None:
            callback(result)
        return

    def select(self, ctx, callback=None):
        self.join(ctx, callback=callback)

    def _goToFunctional(self):
        g_prbCtrlEvents.onPreQueueFunctionalCreated(self.__queueType)
        g_eventDispatcher.showFalloutWindow()


class _FalloutQueueFunctional(prequeue.AccountQueueFunctional):

    @prequeue_storage_getter(QUEUE_TYPE.FALLOUT)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.storage.release(self._queueType)
        g_eventDispatcher.loadFallout()
        return super(_FalloutQueueFunctional, self).init(ctx)

    def fini(self, woEvents=False):
        if not woEvents and self._flags & FUNCTIONAL_FLAG.SWITCH == 0:
            g_eventDispatcher.unloadFallout()
        return super(_FalloutQueueFunctional, self).fini(woEvents)

    @falloutQueueAmmoCheck()
    def queue(self, ctx, callback=None):
        super(_FalloutQueueFunctional, self).queue(ctx, callback=callback)

    def leave(self, ctx, callback=None):
        if ctx.getFlags() & FUNCTIONAL_FLAG.FALLOUT_BATTLES == 0:
            self.storage.suspend()
        super(_FalloutQueueFunctional, self).leave(ctx, callback)

    def doSelectAction(self, action):
        isProcessed = False
        newEntry = None
        name = action.actionName
        if name == PREBATTLE_ACTION_NAME.SQUAD:
            newEntry = unit.FalloutSquadEntry(self.storage.getBattleType(), accountsToInvite=action.accountsToInvite)
            isProcessed = True
        if name == PREBATTLE_ACTION_NAME.FALLOUT:
            g_eventDispatcher.showFalloutWindow()
            isProcessed = True
        elif name == PREBATTLE_ACTION_NAME.FALLOUT_CLASSIC and self._queueType == QUEUE_TYPE.FALLOUT_CLASSIC or name == PREBATTLE_ACTION_NAME.FALLOUT_MULTITEAM and self._queueType == QUEUE_TYPE.FALLOUT_MULTITEAM:
            isProcessed = True
        elif name == PREBATTLE_ACTION_NAME.FALLOUT_QUEUE:
            isProcessed = True
        return SelectResult(isProcessed, newEntry)

    def canPlayerDoAction(self):
        canDo = not self.isInQueue() and self.storage.isEnabled()
        if canDo:
            if self.storage.getBattleType() not in QUEUE_TYPE.FALLOUT:
                return (False, PREBATTLE_RESTRICTION.FALLOUT_NOT_SELECTED)
            if not g_currentVehicle.isPresent():
                return (False, PREBATTLE_RESTRICTION.VEHICLE_GROUP_REQUIRED)
            groupReady, state = g_currentVehicle.item.isGroupReady()
            if not groupReady:
                if state == Vehicle.VEHICLE_STATE.FALLOUT_REQUIRED:
                    return (False, PREBATTLE_RESTRICTION.VEHICLE_GROUP_REQUIRED)
                if state == Vehicle.VEHICLE_STATE.FALLOUT_MIN:
                    return (False, PREBATTLE_RESTRICTION.VEHICLE_GROUP_MIN)
                return (False, PREBATTLE_RESTRICTION.VEHICLE_GROUP_IS_NOT_READY)
        return (canDo, '')

    def getPermissions(self, pID=None, **kwargs):
        assert pID is None, 'Current player has no any player in that mode'
        return FalloutQueuePermissions(self.isInQueue())

    def _makeQueueCtxByAction(self, action=None):
        storage = self.storage
        return pre_queue_ctx.FalloutQueueCtx(self._queueType, storage.getVehiclesInvIDs(excludeEmpty=True), storage.isAutomatch(), waitingID='prebattle/join')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()


class FalloutNoQueueFunctional(_FalloutQueueFunctional):

    def __init__(self, flags=FUNCTIONAL_FLAG.FALLOUT_BATTLES):
        super(FalloutNoQueueFunctional, self).__init__(QUEUE_TYPE.UNKNOWN, _FalloutEventsSubscriber(), flags)

    def _doQueue(self, ctx):
        LOG_ERROR('Do queue is not available for no queue fallout functional')

    def _doDequeue(self, ctx):
        LOG_ERROR('Do dequeue is not available for no queue fallout functional')


class FalloutClassicQueueFunctional(_FalloutQueueFunctional):

    def __init__(self, flags=FUNCTIONAL_FLAG.FALLOUT_BATTLES):
        super(FalloutClassicQueueFunctional, self).__init__(QUEUE_TYPE.FALLOUT_CLASSIC, _FalloutClassicEventsSubscriber(), flags)

    def isInQueue(self):
        return isInFalloutClassic()

    def _doQueue(self, ctx):
        BigWorld.player().enqueueFalloutClassic(ctx.getVehicleInventoryIDs(), canAddToSquad=ctx.canAddToSquad())
        LOG_DEBUG('Sends request on queuing to the fallout classic battles', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueFalloutClassic()
        LOG_DEBUG('Sends request on dequeuing from the fallout classic battles')


class FalloutMultiTeamQueueFunctional(_FalloutQueueFunctional):

    def __init__(self, flags=FUNCTIONAL_FLAG.FALLOUT_BATTLES):
        super(FalloutMultiTeamQueueFunctional, self).__init__(QUEUE_TYPE.FALLOUT_MULTITEAM, _FalloutMultiTeamEventsSubscriber(), flags)

    def isInQueue(self):
        return isInFalloutMultiteam()

    def _doQueue(self, ctx):
        BigWorld.player().enqueueFalloutMultiteam(ctx.getVehicleInventoryIDs(), canAddToSquad=ctx.canAddToSquad())
        LOG_DEBUG('Sends request on queuing to the fallout multiteam battles', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueFalloutMultiteam()
        LOG_DEBUG('Sends request on dequeuing from the fallout multiteam battles')


_BATTLE_TYPE_TO_FUNCTIONAL = {QUEUE_TYPE.FALLOUT_CLASSIC: FalloutClassicQueueFunctional,
 QUEUE_TYPE.FALLOUT_MULTITEAM: FalloutMultiTeamQueueFunctional}

def falloutQueueTypeFactory(battleType):
    return _BATTLE_TYPE_TO_FUNCTIONAL.get(battleType, FalloutNoQueueFunctional)()
