# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/battle_royale/pre_queue/entity.py
import logging
import BigWorld
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from PlayerEvents import g_playerEvents
from constants import QUEUE_TYPE
from gui.prb_control import prb_getters
from helpers import dependency
from gui.ranked_battles.constants import PrimeTimeStatus
from skeletons.gui.game_control import IBattleRoyaleController
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntity, PreQueueEntryPoint
from gui.prb_control.entities.battle_royale.pre_queue.actions_validator import BattleRoyaleActionsValidator
from gui.prb_control.entities.battle_royale.pre_queue.vehicles_watcher import BattleRoyaleVehiclesWatcher
from gui.prb_control.entities.battle_royale.pre_queue.permissions import BattleRoyalePermissions
from gui.prb_control.entities.battle_royale.scheduler import RoyaleScheduler
from gui.prb_control.entities.special_mode.pre_queue import entity as spec_entry
from gui.prb_control.entities.special_mode.pre_queue.ctx import SpecialModeQueueCtx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, PRE_QUEUE_JOIN_ERRORS
from gui.prb_control.storages import prequeue_storage_getter
_logger = logging.getLogger(__name__)

class _BattleRoyaleSubscriber(spec_entry.SpecialModeSubscriber):

    def subscribe(self, entity):
        g_playerEvents.onEnqueuedBattleRoyale += entity.onEnqueued
        g_playerEvents.onDequeuedBattleRoyale += entity.onDequeued
        g_playerEvents.onEnqueuedBattleRoyaleFailure += entity.onEnqueueError
        g_playerEvents.onKickedFromBattleRoyaleQueue += entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena += entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure += entity.onArenaJoinFailure
        super(_BattleRoyaleSubscriber, self).subscribe(entity)

    def unsubscribe(self, entity):
        g_playerEvents.onEnqueuedBattleRoyale -= entity.onEnqueued
        g_playerEvents.onDequeuedBattleRoyale -= entity.onDequeued
        g_playerEvents.onEnqueuedBattleRoyaleFailure -= entity.onEnqueueError
        g_playerEvents.onKickedFromBattleRoyaleQueue -= entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure -= entity.onArenaJoinFailure
        super(_BattleRoyaleSubscriber, self).unsubscribe(entity)


class BattleRoyaleEntryPoint(PreQueueEntryPoint):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self):
        super(BattleRoyaleEntryPoint, self).__init__(FUNCTIONAL_FLAG.BATTLE_ROYALE, QUEUE_TYPE.BATTLE_ROYALE)

    def select(self, ctx, callback=None):
        if not self.__battleRoyaleController.isEnabled():
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.DISABLED)
            return
        else:
            super(BattleRoyaleEntryPoint, self).select(ctx, callback)
            return

    def _getFilterStates(self):
        return (PrimeTimeStatus.NOT_SET,)


class BattleRoyaleEntity(PreQueueEntity):

    def __init__(self):
        super(BattleRoyaleEntity, self).__init__(FUNCTIONAL_FLAG.BATTLE_ROYALE, QUEUE_TYPE.BATTLE_ROYALE, _BattleRoyaleSubscriber())
        self.__watcher = None
        return

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = BattleRoyaleVehiclesWatcher()
        self.__watcher.start()
        result = super(BattleRoyaleEntity, self).init(ctx)
        return result

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        self.storage.suspend()
        if g_currentPreviewVehicle.isPresent():
            reqFlags = FUNCTIONAL_FLAG.LOAD_PAGE | FUNCTIONAL_FLAG.SWITCH | FUNCTIONAL_FLAG.TRAINING
            if ctx and not ctx.hasFlags(reqFlags):
                g_eventDispatcher.loadHangar()
        return super(BattleRoyaleEntity, self).fini(ctx, woEvents)

    def resetPlayerState(self):
        super(BattleRoyaleEntity, self).resetPlayerState()
        g_eventDispatcher.loadHangar()

    @prequeue_storage_getter(QUEUE_TYPE.BATTLE_ROYALE)
    def storage(self):
        return None

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        return SpecialModeQueueCtx(self._queueType, invID, waitingID='prebattle/join')

    def doSelectAction(self, action):
        name = action.actionName
        return SelectResult(True) if name == PREBATTLE_ACTION_NAME.BATTLE_ROYALE else super(BattleRoyaleEntity, self).doSelectAction(action)

    def isInQueue(self):
        return prb_getters.isInBattleRoyaleQueue()

    def getPermissions(self, pID=None, **kwargs):
        return BattleRoyalePermissions(self.isInQueue())

    def _createActionsValidator(self):
        return BattleRoyaleActionsValidator(self)

    def _createScheduler(self):
        return RoyaleScheduler(self)

    def _doQueue(self, ctx):
        BigWorld.player().enqueueBattleRoyale(ctx.getVehicleInventoryID())
        _logger.debug('Sends request on queuing to the Battle Royale - %r', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueBattleRoyale()
        _logger.debug('Sends request on dequeuing from the Battle Royale')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()
