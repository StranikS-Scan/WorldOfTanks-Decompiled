# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/prb_control/entities/regular/pre_queue/entity.py
import logging
import BigWorld
from CurrentVehicle import g_currentVehicle
from constants import QUEUE_TYPE
from skeletons.gui.game_control import IBattleRoyaleController
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from battle_royale.gui.prb_control.entities.regular import isNeedToLoadHangar
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntity, PreQueueEntryPoint, PreQueueSubscriber
from battle_royale.gui.prb_control.entities.regular.pre_queue.actions_validator import BattleRoyaleActionsValidator
from battle_royale.gui.prb_control.entities.regular.pre_queue.vehicles_watcher import BattleRoyaleVehiclesWatcher
from battle_royale.gui.prb_control.entities.regular.pre_queue.permissions import BattleRoyalePermissions
from battle_royale.gui.prb_control.entities.regular.scheduler import RoyaleScheduler
from gui.prb_control.entities.special_mode.pre_queue.ctx import SpecialModeQueueCtx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, PRE_QUEUE_JOIN_ERRORS
from gui.prb_control.storages import prequeue_storage_getter
from gui.periodic_battles.models import PrimeTimeStatus
from helpers import dependency
_logger = logging.getLogger(__name__)

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
        super(BattleRoyaleEntity, self).__init__(FUNCTIONAL_FLAG.BATTLE_ROYALE, QUEUE_TYPE.BATTLE_ROYALE, PreQueueSubscriber())
        self.__watcher = None
        self.storage = prequeue_storage_getter(QUEUE_TYPE.BATTLE_ROYALE)()
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
        if isNeedToLoadHangar(ctx):
            g_eventDispatcher.loadHangar()
        return super(BattleRoyaleEntity, self).fini(ctx, woEvents)

    def resetPlayerState(self):
        super(BattleRoyaleEntity, self).resetPlayerState()
        g_eventDispatcher.loadHangar()

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        return SpecialModeQueueCtx(self._queueType, invID, waitingID='prebattle/join')

    def doSelectAction(self, action):
        name = action.actionName
        return SelectResult(True) if name == PREBATTLE_ACTION_NAME.BATTLE_ROYALE else super(BattleRoyaleEntity, self).doSelectAction(action)

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
