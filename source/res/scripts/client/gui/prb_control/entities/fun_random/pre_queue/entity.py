# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fun_random/pre_queue/entity.py
import logging
import typing
import BigWorld
from CurrentVehicle import g_currentVehicle
from constants import QUEUE_TYPE
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntryPoint, PreQueueSubscriber, PreQueueEntity
from gui.prb_control.entities.fun_random.pre_queue.actions_validator import FunRandomActionsValidator
from gui.prb_control.entities.fun_random.pre_queue.ctx import FunRandomQueueCtx
from gui.prb_control.entities.fun_random.pre_queue.permissions import FunRandomPermissions
from gui.prb_control.entities.fun_random.pre_queue.scheduler import FunRandomScheduler
from gui.prb_control.entities.fun_random.pre_queue.vehicles_watcher import FunRandomVehiclesWatcher
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, PRE_QUEUE_JOIN_ERRORS
from gui.prb_control.storages import prequeue_storage_getter
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController
if typing.TYPE_CHECKING:
    from gui.prb_control.storages.local_storage import LocalStorage
_logger = logging.getLogger(__name__)

class FunRandomEntryPoint(PreQueueEntryPoint):
    __funRandomController = dependency.descriptor(IFunRandomController)

    def __init__(self):
        super(FunRandomEntryPoint, self).__init__(FUNCTIONAL_FLAG.FUN_RANDOM, QUEUE_TYPE.FUN_RANDOM)

    def select(self, ctx, callback=None):
        if not self.__funRandomController.isEnabled():
            _logger.warning('Trying to get into fun random pre queue when event is disabled')
            self.__abortSelection(PRE_QUEUE_JOIN_ERRORS.DISABLED, callback)
        elif not self.__funRandomController.isAvailable():
            _logger.debug('Trying to get into fun random pre queue when event is not available')
            self.__abortSelection(PRE_QUEUE_JOIN_ERRORS.NOT_AVAILABLE, callback)
        else:
            super(FunRandomEntryPoint, self).select(ctx, callback)

    def __abortSelection(self, reason, callback=None):
        if callback is not None:
            callback(False)
        g_prbCtrlEvents.onPreQueueJoinFailure(reason)
        return


class FunRandomEntity(PreQueueEntity):

    def __init__(self):
        super(FunRandomEntity, self).__init__(FUNCTIONAL_FLAG.FUN_RANDOM, QUEUE_TYPE.FUN_RANDOM, PreQueueSubscriber())
        self.__watcher = None
        return

    @prequeue_storage_getter(QUEUE_TYPE.FUN_RANDOM)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = FunRandomVehiclesWatcher()
        self.__watcher.start()
        return super(FunRandomEntity, self).init(ctx)

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        if not woEvents and not self.canSwitch(ctx) and (ctx is None or not ctx.hasFlags(FUNCTIONAL_FLAG.LOAD_PAGE)):
            g_eventDispatcher.loadHangar()
        return super(FunRandomEntity, self).fini(ctx, woEvents)

    def getPermissions(self, pID=None, **kwargs):
        return FunRandomPermissions(self.isInQueue())

    def doSelectAction(self, action):
        return SelectResult(True, None) if action.actionName == PREBATTLE_ACTION_NAME.FUN_RANDOM else super(FunRandomEntity, self).doSelectAction(action)

    def leave(self, ctx, callback=None):
        self.storage.suspend()
        super(FunRandomEntity, self).leave(ctx, callback)

    @vehicleAmmoCheck
    def queue(self, ctx, callback=None):
        super(FunRandomEntity, self).queue(ctx, callback=callback)

    def _createActionsValidator(self):
        return FunRandomActionsValidator(self)

    def _createScheduler(self):
        return FunRandomScheduler(self)

    def _doQueue(self, ctx):
        BigWorld.player().enqueueFunRandom(ctx.getVehicleInventoryID())
        _logger.debug('Sends request for queuing to the fun event battle %s', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueFunRandom()
        _logger.debug('Sends request for dequeueing from the fun event battle')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        return FunRandomQueueCtx(invID, waitingID='prebattle/join')
