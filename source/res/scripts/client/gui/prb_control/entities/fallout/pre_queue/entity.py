# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fallout/pre_queue/entity.py
import BigWorld
from PlayerEvents import g_playerEvents
from constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.prb_control.entities.fallout.pre_queue.actions_validator import FalloutActionsValidator
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntity, PreQueueEntryPoint
from gui.prb_control.entities.fallout import falloutQueueAmmoCheck
from gui.prb_control.entities.fallout.pre_queue.ctx import FalloutQueueCtx
from gui.prb_control.entities.fallout.pre_queue.permissions import FalloutPermissions
from gui.prb_control.entities.fallout.squad.entity import FalloutSquadEntryPoint
from gui.prb_control.items import SelectResult
from gui.prb_control.prb_getters import isInFalloutClassic, isInFalloutMultiteam
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from gui.prb_control.storages import prequeue_storage_getter

class NoFalloutSubscriber(PreQueueSubscriber):

    def subscribe(self, entity):
        pass

    def unsubscribe(self, entity):
        pass


class FalloutClassicSubscriber(PreQueueSubscriber):

    def subscribe(self, entity):
        g_playerEvents.onEnqueuedFalloutClassic += entity.onEnqueued
        g_playerEvents.onDequeuedFalloutClassic += entity.onDequeued
        g_playerEvents.onEnqueueFalloutClassicFailure += entity.onEnqueueError
        g_playerEvents.onKickedFromFalloutClassic += entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena += entity.onKickedFromArena

    def unsubscribe(self, entity):
        g_playerEvents.onEnqueuedFalloutClassic -= entity.onEnqueued
        g_playerEvents.onDequeuedFalloutClassic -= entity.onDequeued
        g_playerEvents.onEnqueueFalloutClassicFailure -= entity.onEnqueueError
        g_playerEvents.onKickedFromFalloutClassic -= entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= entity.onKickedFromArena


class FalloutMultiTeamSubscriber(PreQueueSubscriber):

    def subscribe(self, entity):
        g_playerEvents.onEnqueuedFalloutMultiteam += entity.onEnqueued
        g_playerEvents.onDequeuedFalloutMultiteam += entity.onDequeued
        g_playerEvents.onEnqueueFalloutMultiteamFailure += entity.onEnqueueError
        g_playerEvents.onKickedFromFalloutMultiteam += entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena += entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure += entity.onArenaJoinFailure

    def unsubscribe(self, entity):
        g_playerEvents.onEnqueuedFalloutMultiteam -= entity.onEnqueued
        g_playerEvents.onDequeuedFalloutMultiteam -= entity.onDequeued
        g_playerEvents.onEnqueueFalloutMultiteamFailure -= entity.onEnqueueError
        g_playerEvents.onKickedFromFalloutMultiteam -= entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure -= entity.onArenaJoinFailure


class _FalloutBaseEntryPoint(PreQueueEntryPoint):

    def __init__(self, queueType):
        super(_FalloutBaseEntryPoint, self).__init__(FUNCTIONAL_FLAG.FALLOUT, queueType)

    def _goToEntity(self):
        super(_FalloutBaseEntryPoint, self)._goToEntity()
        g_eventDispatcher.showFalloutWindow()


class NoFalloutEntryPoint(_FalloutBaseEntryPoint):

    def __init__(self):
        super(NoFalloutEntryPoint, self).__init__(QUEUE_TYPE.UNKNOWN)


class FalloutClassicEntryPoint(_FalloutBaseEntryPoint):

    def __init__(self):
        super(FalloutClassicEntryPoint, self).__init__(QUEUE_TYPE.FALLOUT_CLASSIC)


class FalloutMultiTeamEntryPoint(_FalloutBaseEntryPoint):

    def __init__(self):
        super(FalloutMultiTeamEntryPoint, self).__init__(QUEUE_TYPE.FALLOUT_MULTITEAM)


class _FalloutEntity(PreQueueEntity):

    def __init__(self, queueType, subscriber):
        super(_FalloutEntity, self).__init__(FUNCTIONAL_FLAG.FALLOUT, queueType, subscriber)

    @prequeue_storage_getter(QUEUE_TYPE.FALLOUT)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.storage.release(self._queueType)
        g_eventDispatcher.loadFallout()
        return super(_FalloutEntity, self).init(ctx)

    def fini(self, ctx=None, woEvents=False):
        if not woEvents:
            if not self.canSwitch(ctx):
                g_eventDispatcher.removeFalloutFromCarousel()
        else:
            g_eventDispatcher.removeFalloutFromCarousel(closeWindow=False)
        return super(_FalloutEntity, self).fini(ctx, woEvents)

    @falloutQueueAmmoCheck()
    def queue(self, ctx, callback=None):
        super(_FalloutEntity, self).queue(ctx, callback=callback)

    def leave(self, ctx, callback=None):
        if not self.canSwitch(ctx):
            self.storage.suspend()
        super(_FalloutEntity, self).leave(ctx, callback)

    def doSelectAction(self, action):
        name = action.actionName
        if name == PREBATTLE_ACTION_NAME.SQUAD:
            return SelectResult(True, FalloutSquadEntryPoint(self.storage.getBattleType(), accountsToInvite=action.accountsToInvite))
        if name == PREBATTLE_ACTION_NAME.FALLOUT:
            g_eventDispatcher.showFalloutWindow()
            return SelectResult(True)
        return super(_FalloutEntity, self).doSelectAction(action)

    def getPermissions(self, pID=None, **kwargs):
        assert pID is None, 'Current player has no any player in that mode'
        return FalloutPermissions(self.isInQueue())

    def _createActionsValidator(self):
        return FalloutActionsValidator(self)

    def _makeQueueCtxByAction(self, action=None):
        storage = self.storage
        return FalloutQueueCtx(self._queueType, storage.getVehiclesInvIDs(excludeEmpty=True), storage.isAutomatch(), waitingID='prebattle/join')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()


class NoFalloutEntity(_FalloutEntity):

    def __init__(self):
        super(NoFalloutEntity, self).__init__(QUEUE_TYPE.UNKNOWN, NoFalloutSubscriber())

    def _doQueue(self, ctx):
        LOG_ERROR('Do queue is not available for no pre queue fallout entity')

    def _doDequeue(self, ctx):
        LOG_ERROR('Do dequeue is not available for no pre queue fallout entity')


class FalloutClassicEntity(_FalloutEntity):

    def __init__(self):
        super(FalloutClassicEntity, self).__init__(QUEUE_TYPE.FALLOUT_CLASSIC, FalloutClassicSubscriber())

    def isInQueue(self):
        return isInFalloutClassic()

    def doSelectAction(self, action):
        name = action.actionName
        return SelectResult(True) if name == PREBATTLE_ACTION_NAME.FALLOUT_CLASSIC else super(FalloutClassicEntity, self).doSelectAction(action)

    def _doQueue(self, ctx):
        BigWorld.player().enqueueFalloutClassic(ctx.getVehicleInventoryIDs(), canAddToSquad=ctx.canAddToSquad())
        LOG_DEBUG('Sends request on queuing to the fallout classic battles', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueFalloutClassic()
        LOG_DEBUG('Sends request on dequeuing from the fallout classic battles')


class FalloutMultiTeamEntity(_FalloutEntity):

    def __init__(self):
        super(FalloutMultiTeamEntity, self).__init__(QUEUE_TYPE.FALLOUT_MULTITEAM, FalloutMultiTeamSubscriber())

    def isInQueue(self):
        return isInFalloutMultiteam()

    def doSelectAction(self, action):
        name = action.actionName
        return SelectResult(True) if name == PREBATTLE_ACTION_NAME.FALLOUT_MULTITEAM else super(FalloutMultiTeamEntity, self).doSelectAction(action)

    def _doQueue(self, ctx):
        BigWorld.player().enqueueFalloutMultiteam(ctx.getVehicleInventoryIDs(), canAddToSquad=ctx.canAddToSquad())
        LOG_DEBUG('Sends request on queuing to the fallout multiteam battles', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueFalloutMultiteam()
        LOG_DEBUG('Sends request on dequeuing from the fallout multiteam battles')


_BATTLE_TYPE_TO_FUNCTIONAL = {QUEUE_TYPE.FALLOUT_CLASSIC: FalloutClassicEntity,
 QUEUE_TYPE.FALLOUT_MULTITEAM: FalloutMultiTeamEntity}

def falloutQueueTypeFactory(battleType):
    return _BATTLE_TYPE_TO_FUNCTIONAL.get(battleType, NoFalloutEntity)()
