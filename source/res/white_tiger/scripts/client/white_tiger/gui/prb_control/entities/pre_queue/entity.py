# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/entities/pre_queue/entity.py
import logging
import BigWorld
from soft_exception import SoftException
from shared_utils import nextTick
from constants import QUEUE_TYPE
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntryPoint, PreQueueEntity, PreQueueSubscriber
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PRE_QUEUE_JOIN_ERRORS
from gui.prb_control.storages import prequeue_storage_getter
from gui.periodic_battles.models import PrimeTimeStatus
from skeletons.prebattle_vehicle import IPrebattleVehicle
from helpers import dependency
from skeletons.gui.game_control import IWhiteTigerController
from white_tiger.gui.prb_control.entities import isHangarShallBeLoaded
from white_tiger.gui.gui_constants import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from white_tiger.gui.prb_control.entities.pre_queue.ctx import WhiteTigerBattleQueueCtx
from white_tiger.gui.prb_control.entities.pre_queue.scheduler import WhiteTigerScheduler
from white_tiger.gui.prb_control.entities.pre_queue.vehicles_watcher import WhiteTigerBattlesVehiclesWatcher
from white_tiger.gui.prb_control.entities.pre_queue.actions_validator import WhiteTigerBattleActionsValidator
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(ctrl=IWhiteTigerController)
def canSelectPrbEntity(ctrl=None):
    return ctrl.isAvailable()


class WhiteTigerEntryPoint(PreQueueEntryPoint):
    __wtController = dependency.descriptor(IWhiteTigerController)

    def __init__(self):
        super(WhiteTigerEntryPoint, self).__init__(FUNCTIONAL_FLAG.WHITE_TIGER, QUEUE_TYPE.WHITE_TIGER)

    def select(self, ctx, callback=None):
        status, _, _ = self.__wtController.getPrimeTimeStatus()
        if status == PrimeTimeStatus.FROZEN:
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.DISABLED)
            return
        else:
            super(WhiteTigerEntryPoint, self).select(ctx, callback)
            return


class WhiteTigerBattleEntity(PreQueueEntity):
    prebattleVehicle = dependency.descriptor(IPrebattleVehicle)

    def __init__(self):
        super(WhiteTigerBattleEntity, self).__init__(FUNCTIONAL_FLAG.WHITE_TIGER, QUEUE_TYPE.WHITE_TIGER, PreQueueSubscriber())
        self.__watcher = None
        self.__waitForRequeue = False
        return

    def init(self, ctx=None):
        self.__watcher = WhiteTigerBattlesVehiclesWatcher()
        self.__watcher.start()
        g_eventDispatcher.loadHangar()
        return super(WhiteTigerBattleEntity, self).init(ctx=ctx)

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        self.storage.suspend()
        if not woEvents and isHangarShallBeLoaded(ctx):
            g_eventDispatcher.loadHangar()
        return super(WhiteTigerBattleEntity, self).fini(ctx, woEvents)

    @property
    def storage(self):
        return prequeue_storage_getter(QUEUE_TYPE.WHITE_TIGER)()

    def doSelectAction(self, action):
        return SelectResult(True) if action.actionName in (PREBATTLE_ACTION_NAME.WHITE_TIGER,) else super(WhiteTigerBattleEntity, self).doSelectAction(action)

    @vehicleAmmoCheck
    def queue(self, ctx, callback=None):
        super(WhiteTigerBattleEntity, self).queue(ctx, callback=callback)

    def leave(self, ctx, callback=None):
        super(WhiteTigerBattleEntity, self).leave(ctx, callback=callback)

    def requeue(self, vehicle):
        if not self.isInQueue():
            raise SoftException('Player is not in the queue')
        self.prebattleVehicle.select(vehicle)
        self.__waitForRequeue = True
        self.doAction()

    def onEnqueued(self, *args):
        super(WhiteTigerBattleEntity, self).onEnqueued(*args)
        self.__waitForRequeue = False

    def onDequeued(self, *args):
        super(WhiteTigerBattleEntity, self).onDequeued(*args)
        if self.__waitForRequeue:
            self.__waitForRequeue = False
            nextTick(self.doAction)()

    def _createActionsValidator(self):
        return WhiteTigerBattleActionsValidator(self)

    def _createScheduler(self):
        return WhiteTigerScheduler(self)

    def _doQueue(self, ctx):
        BigWorld.player().AccountWhiteTigerComponent.enqueue(ctx.getVehicleInventoryID())
        _logger.debug('Sends request on queuing to the WhiteTiger battles %s', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().AccountWhiteTigerComponent.dequeue()
        _logger.debug('Sends request on dequeuing from the WhiteTiger')

    def _makeQueueCtxByAction(self, action=None):
        vehicle = self.prebattleVehicle.item
        if not vehicle:
            raise SoftException('Vehicle cannot be None')
        invID = vehicle.invID
        if not invID:
            raise SoftException('Inventory ID of vehicle can not be zero')
        return WhiteTigerBattleQueueCtx(vehInvID=invID, waitingID='prebattle/join')

    def _goToQueueUI(self):
        g_eventDispatcher.loadEventBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()
